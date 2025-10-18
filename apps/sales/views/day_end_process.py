from django.http import JsonResponse
from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction, connection
from django.utils import timezone
from datetime import datetime
from apps.utils.voucher_generator import generate_voucher_number
import logging

# Set up logging
logger = logging.getLogger(__name__)


class DayEndProcess(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'day_end_process'
    template_name = 'day_end_process.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle day end process POST request
        """
        try:
            # Get parameters
            xdate = request.POST.get('xdate')
            current_zid = request.session.get('current_zid')
            session_user = request.session.get('username', 'admin@fixit.com')

            # Validate inputs
            if not xdate:
                return JsonResponse({
                    'success': False,
                    'message': 'Process date is required'
                }, status=400)

            if not current_zid:
                return JsonResponse({
                    'success': False,
                    'message': 'No business context found'
                }, status=400)

            # Execute day end process
            with transaction.atomic():
                result = self.execute_day_end_process(current_zid, xdate, session_user)

                if result['success']:
                    return JsonResponse({
                        'success': True,
                        'message': f'Day end process completed successfully. Voucher: {result["voucher"]}',
                        'voucher': result['voucher']
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': result['message']
                    }, status=400)

        except Exception as e:
            logger.error(f"Day end process error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Day end process failed: {str(e)}'
            }, status=500)

    def execute_day_end_process(self, zid, xdate, session_user):
        """
        Execute the complete day end process
        """
        try:
            logger.info(f"Starting day end process for zid={zid}, xdate={xdate}")

            # Step 1: Acquire PostgreSQL advisory lock to prevent concurrent processing
            with connection.cursor() as cursor:
                lock_key = self.get_lock_key(zid, xdate)
                cursor.execute("SELECT pg_advisory_xact_lock(%s)", [lock_key])

                # Step 2: Check for duplicate processing (after acquiring lock)
                duplicate_check = self.check_duplicate_processing(zid, xdate)
                if duplicate_check['is_duplicate']:
                    logger.info(f"Duplicate processing detected for {xdate}. Voucher: {duplicate_check['voucher']}")
                    return {
                        'success': False,
                        'message': f'Day end process already completed for {xdate}. Voucher: {duplicate_check["voucher"]}'
                    }

            # Step 3: Aggregate data from opordnview
            aggregated_data = self.aggregate_sales_data(zid, xdate)

            if not aggregated_data:
                logger.error(f"No sales data found for date {xdate}")
                return {
                    'success': False,
                    'message': 'No sales data found for the specified date'
                }

            # Step 4: Generate voucher number
            voucher = generate_voucher_number(zid, 'SALE', 'glheader', 'xvoucher')

            # Step 5: Insert GL header
            self.insert_gl_header(zid, voucher, xdate, session_user)

            # Step 6: Insert GL details
            self.insert_gl_details(zid, voucher, xdate, aggregated_data)

            logger.info("Day end process completed successfully")
            return {
                'success': True,
                'voucher': voucher,
                'message': 'Day end process completed successfully'
            }

        except Exception as e:
            logger.error(f"Execute day end process error: {str(e)}")
            raise

    def check_duplicate_processing(self, zid, xdate):
        """
        Check if day end process already completed for this date
        """
        with connection.cursor() as cursor:
            # Check for existing voucher with the specific reference pattern
            xref = f"***System generated Sales voucher on {xdate}"

            cursor.execute("""
                SELECT xvoucher FROM glheader
                WHERE zid = %s AND xref = %s AND xtrngl = 'SALE'
                LIMIT 1
            """, [zid, xref])

            result = cursor.fetchone()
            if result and len(result) > 0:
                return {
                    'is_duplicate': True,
                    'voucher': result[0]
                }

            return {'is_duplicate': False}

    def get_lock_key(self, zid, xdate):
        """
        Generate a unique lock key for PostgreSQL advisory lock
        """
        # Create a simple hash of zid + xdate to get a consistent integer key
        hash_input = f"{zid}_{xdate}"
        # Convert to a simple integer within PostgreSQL bigint range
        return hash(hash_input) % (2**31 - 1)

    def aggregate_sales_data(self, zid, xdate):
        """
        Aggregate sales data from opordnview
        """
        with connection.cursor() as cursor:
            # Get total amount
            cursor.execute("""
                SELECT COALESCE(SUM(xtotamt), 0) as total_amt
                FROM opordnview
                WHERE zid = %s AND xdate = %s
            """, [zid, xdate])
            total_result = cursor.fetchone()
            total_amt = total_result[0] if total_result else 0

            # Get cash amount
            cursor.execute("""
                SELECT COALESCE(SUM(xlineamt), 0) as cash_amt
                FROM opordnview
                WHERE zid = %s AND xdate = %s
            """, [zid, xdate])
            cash_result = cursor.fetchone()
            cash_amt = cash_result[0] if cash_result else 0

            # Get bank amounts by xsalescat
            cursor.execute("""
                SELECT xsalescat, COALESCE(SUM(xdtcomm), 0) as bank_amt
                FROM opordnview
                WHERE zid = %s AND xdate = %s AND xsltype = 'Card Sale'
                GROUP BY xsalescat
            """, [zid, xdate])
            bank_data = cursor.fetchall()

            # Get discount amount
            cursor.execute("""
                SELECT COALESCE(SUM(xdtdisc), 0) + COALESCE(SUM(xdiscf), 0) as disc_amt
                FROM opordnview
                WHERE zid = %s AND xdate = %s
            """, [zid, xdate])
            disc_result = cursor.fetchone()
            disc_amt = disc_result[0] if disc_result else 0

            return {
                'total_amt': total_amt,
                'cash_amt': cash_amt,
                'bank_data': bank_data,
                'disc_amt': disc_amt
            }

    def insert_gl_header(self, zid, voucher, xdate, session_user):
        """
        Insert GL header record
        """
        # Parse date to extract year and month
        date_obj = datetime.strptime(xdate, '%Y-%m-%d')
        year = date_obj.year
        month = f"{date_obj.month:02d}"

        current_timestamp = timezone.now()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO glheader (
                    ztime, zid, xvoucher, xref, xdate, xlong, xpostflag,
                    xyear, xper, xstatusjv, xdatedue, xnumofper, xtrngl,
                    xmember, xapproved, xaction
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                current_timestamp,  # ztime
                zid,  # zid
                voucher,  # xvoucher
                f"***System generated Sales voucher on {xdate}",  # xref
                xdate,  # xdate
                f"** Created By System On {xdate} **",  # xlong
                True,  # xpostflag
                year,  # xyear
                month,  # xper
                "Balanced",  # xstatusjv
                xdate,  # xdatedue
                0,  # xnumofper
                "SALE",  # xtrngl
                session_user,  # xmember
                1,  # xapproved
                "Journal"  # xaction
            ])

    def insert_gl_details(self, zid, voucher, xdate, aggregated_data):
        """
        Insert all GL detail records
        """
        logger.info(f"Starting GL details insertion for voucher: {voucher}")
        current_timestamp = timezone.now()
        row_number = 20

        # Bank mapping - using parent account 01020001 for all banks
        bank_mapping = {
            'PBL': '01020001',
            'DBBL': '01020001',
            'CBL': '01020001',
            'MTBL': '01020001',
            'UCB': '01020001'
        }

        # Sub-account codes for each bank
        bank_sub_mapping = {
            'PBL': '0102000101',
            'DBBL': '0102000102',
            'CBL': '0102000103',
            'MTBL': '0102000104',
            'UCB': '0102000105'
        }

        with connection.cursor() as cursor:
            # Get project code
            cursor.execute("""
                SELECT xcode FROM xcodes
                WHERE zid = %s AND xtype = 'Project'
                LIMIT 1
            """, [zid])
            project_result = cursor.fetchone()
            project_code = project_result[0] if project_result else "HMBR FIXIT GULSHAN"

            # Get sales account
            cursor.execute("""
                SELECT xacc FROM glmst
                WHERE xdesc = 'Sales' AND zid = %s
                LIMIT 1
            """, [zid])
            sales_account_result = cursor.fetchone()
            sales_account = sales_account_result[0] if sales_account_result else "08010001"

            # Get cash account
            cursor.execute("""
                SELECT xacc FROM glmst
                WHERE xdesc = 'Cash' AND zid = %s
                LIMIT 1
            """, [zid])
            cash_account_result = cursor.fetchone()
            cash_account = cash_account_result[0] if cash_account_result else "01010001"

            # 1. Sales Revenue Entry (Credit)
            self.insert_gl_detail_row(
                cursor, current_timestamp, zid, voucher, row_number,
                sales_account, "Ledger", "None", project_code, "BDT",
                -aggregated_data['total_amt'], -aggregated_data['total_amt'],
                "Income", voucher, xdate, xdate, xdate
            )
            row_number += 10

            # 2. Cash Entry (Debit)
            if aggregated_data['cash_amt'] > 0:
                self.insert_gl_detail_row(
                    cursor, current_timestamp, zid, voucher, row_number,
                    cash_account, "Cash", "None", project_code, "BDT",
                    aggregated_data['cash_amt'], aggregated_data['cash_amt'],
                    "Asset", voucher, xdate, xdate, xdate
                )
                row_number += 10

            # 3. Bank Entries (Debit)
            for bank_code, bank_amount in aggregated_data['bank_data']:
                if bank_amount > 0 and bank_code in bank_mapping and bank_code in bank_sub_mapping:
                    bank_account = bank_mapping[bank_code]
                    bank_sub_account = bank_sub_mapping[bank_code]
                    self.insert_gl_detail_row(
                        cursor, current_timestamp, zid, voucher, row_number,
                        bank_account, "Bank", "Subaccount", project_code, "BDT",
                        bank_amount, bank_amount, "Asset", voucher, xdate, xdate, xdate,
                        xsub=bank_sub_account
                    )
                    row_number += 10
                else:
                    logger.warning(f"Skipping bank entry {bank_code}: amount={bank_amount}, mapping_exists={bank_code in bank_mapping and bank_code in bank_sub_mapping}")

            # 4. Discount Entry (Debit)
            if aggregated_data['disc_amt'] > 0:
                # Get discount account
                try:
                    cursor.execute("""
                        SELECT xacc FROM glmst
                        WHERE xdesc LIKE '%Discount%' AND zid = %s
                        LIMIT 1
                    """, [zid])
                    discount_account_result = cursor.fetchone()
                    discount_account = discount_account_result[0] if discount_account_result else "07080001"
                except Exception as e:
                    logger.error(f"Error getting discount account: {str(e)}")
                    discount_account = "07080001"

                self.insert_gl_detail_row(
                    cursor, current_timestamp, zid, voucher, row_number,
                    discount_account, "Ledger", "Customer", project_code, "BDT",
                    aggregated_data['disc_amt'], aggregated_data['disc_amt'],
                    "Expenditure", voucher, xdate, xdate, xdate
                )

    def insert_gl_detail_row(self, cursor, ztime, zid, xvoucher, xrow, xacc,
                           xaccusage, xaccsource, xproj, xcur, xprime, xbase,
                           xacctype, xinvnum, xdateapp, xdateclr, xdatedue, xsub=None):
        """
        Insert a single GL detail row
        """
        try:
            cursor.execute("""
                INSERT INTO gldetail (
                    ztime, zid, xvoucher, xrow, xacc, xaccusage, xaccsource,
                    xproj, xcur, xexch, xprime, xbase, xacctype, xinvnum,
                    xdateapp, xexchval, xdateclr, xdatedue, xsub
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                ztime, zid, xvoucher, xrow, xacc, xaccusage, xaccsource,
                xproj, xcur, 1, xprime, xbase, xacctype, xinvnum,
                xdateapp, 1, xdateclr, xdatedue, xsub
            ])
        except Exception as e:
            logger.error(f"Error inserting GL detail row: {str(e)}")
            logger.error(f"Parameters: voucher={xvoucher}, row={xrow}, account={xacc}")
            raise

@csrf_exempt
@login_required
def delete_day_end_process(request, date):
    """
    Delete day-end process entries for a specific date
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST method allowed'})

    try:
        # Get current user's zid
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({'success': False, 'message': 'No business selected'})

        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'})

        with transaction.atomic():
            with connection.cursor() as cursor:
                # Find xvoucher from glheader for the specific date and zid
                xref = f"***System generated Sales voucher on {date}"
                cursor.execute("""
                    SELECT xvoucher FROM glheader
                    WHERE zid = %s AND xref = %s AND xtrngl = 'SALE'
                    LIMIT 1
                """, [current_zid, xref])

                result = cursor.fetchone()
                if not result:
                    return JsonResponse({
                        'success': False,
                        'message': f'No day-end process found for date {date}'
                    })

                xvoucher = result[0]

                # Delete from gldetail first (child records)
                cursor.execute("""
                    DELETE FROM gldetail
                    WHERE zid = %s AND xvoucher = %s
                """, [current_zid, xvoucher])

                detail_deleted = cursor.rowcount

                # Delete from glheader (parent record)
                cursor.execute("""
                    DELETE FROM glheader
                    WHERE zid = %s AND xvoucher = %s
                """, [current_zid, xvoucher])

                header_deleted = cursor.rowcount

                if header_deleted == 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'Failed to delete day-end process entries'
                    })

                logger.info(f"Day-end process deleted successfully for date {date}, voucher {xvoucher}")
                logger.info(f"Deleted {detail_deleted} detail records and {header_deleted} header record")

                return JsonResponse({
                    'success': True,
                    'message': f'Day-end process for {date} deleted successfully',
                    'voucher': xvoucher,
                    'details_deleted': detail_deleted,
                    'headers_deleted': header_deleted
                })

    except Exception as e:
        logger.error(f"Delete day-end process error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error deleting day-end process: {str(e)}'
        })
