from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection, transaction
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
@transaction.atomic
def update_transaction_api(request):
    """
    API endpoint to update an existing sales transaction
    """
    try:
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({
                'success': False,
                'message': 'No business context found'
            }, status=400)

        # Parse JSON data
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        header_data = data.get('header', {})
        items_data = data.get('items', [])

        if not transaction_id:
            return JsonResponse({
                'success': False,
                'message': 'Transaction ID is required'
            }, status=400)

        if not items_data:
            return JsonResponse({
                'success': False,
                'message': 'At least one item is required'
            }, status=400)

        # Validate transaction exists and belongs to current zid
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM opord 
                WHERE zid = %s AND xordernum = %s
            """, [current_zid, transaction_id])
            
            if cursor.fetchone()[0] == 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Transaction not found or access denied'
                }, status=404)

        # Update transaction header (opord table)
        update_header_result = update_transaction_header(
            current_zid, transaction_id, header_data
        )
        
        if not update_header_result['success']:
            return JsonResponse(update_header_result, status=400)

        # Update transaction items (opodt table)
        update_items_result = update_transaction_items(
            current_zid, transaction_id, items_data
        )
        
        if not update_items_result['success']:
            return JsonResponse(update_items_result, status=400)

        logger.info(f"Transaction {transaction_id} updated successfully by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Transaction updated successfully',
            'transaction_id': transaction_id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error updating transaction: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while updating the transaction'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
@transaction.atomic
def delete_transaction_api(request):
    """
    API endpoint to delete a sales transaction
    """
    try:
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({
                'success': False,
                'message': 'No business context found'
            }, status=400)

        transaction_id = request.POST.get('transaction_id')
        
        if not transaction_id:
            return JsonResponse({
                'success': False,
                'message': 'Transaction ID is required'
            }, status=400)

        # Validate transaction exists and belongs to current zid
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT xstatusord FROM opord 
                WHERE zid = %s AND xordernum = %s
            """, [current_zid, transaction_id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({
                    'success': False,
                    'message': 'Transaction not found or access denied'
                }, status=404)

            # Check if transaction can be deleted (only allow deletion of certain statuses)
            status = result[0]
            if status in ['Confirmed', 'Delivered']:
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot delete transaction with status: {status}'
                }, status=400)

        # Delete transaction items first (opodt table)
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM opodt 
                WHERE zid = %s AND xordernum = %s
            """, [current_zid, transaction_id])
            
            items_deleted = cursor.rowcount
            logger.info(f"Deleted {items_deleted} items for transaction {transaction_id}")

        # Delete transaction header (opord table)
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM opord 
                WHERE zid = %s AND xordernum = %s
            """, [current_zid, transaction_id])
            
            if cursor.rowcount == 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to delete transaction'
                }, status=500)

        logger.info(f"Transaction {transaction_id} deleted successfully by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Transaction deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while deleting the transaction'
        }, status=500)


def update_transaction_header(zid, transaction_id, header_data):
    """
    Update transaction header in opord table
    """
    try:
        with connection.cursor() as cursor:
            # Build dynamic update query based on provided data
            update_fields = []
            params = []
            
            # Map form fields to database columns
            field_mapping = {
                'xdate': 'xdate',
                'xcus': 'xcus',
                'customer_name': 'xorg',  # Assuming customer name goes to xorg
                'xwh': 'xwh',
                'xsp': 'xsp',
                'xmobile': 'xmobile',
                'xstatusord': 'xstatusord',
                'xsltype': 'xsltype',
                'xsalescat': 'xsalescat',  # Bank name
                'xdocnum': 'xdocnum',     # Card number
                'xdtcomm': 'xdtcomm'      # Card amount
            }
            
            for form_field, db_field in field_mapping.items():
                if form_field in header_data:
                    update_fields.append(f"{db_field} = %s")
                    params.append(header_data[form_field])
            
            if not update_fields:
                return {'success': True, 'message': 'No header fields to update'}
            
            # Add WHERE clause parameters
            params.extend([zid, transaction_id])
            
            query = f"""
                UPDATE opord 
                SET {', '.join(update_fields)}
                WHERE zid = %s AND xordernum = %s
            """
            
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                return {
                    'success': False,
                    'message': 'Transaction header not found or no changes made'
                }
            
            return {'success': True, 'message': 'Header updated successfully'}
            
    except Exception as e:
        logger.error(f"Error updating transaction header: {str(e)}")
        return {
            'success': False,
            'message': f'Error updating header: {str(e)}'
        }


def update_transaction_items(zid, transaction_id, items_data):
    """
    Update transaction items in opodt table
    """
    try:
        with connection.cursor() as cursor:
            # First, delete existing items for this transaction
            cursor.execute("""
                DELETE FROM opodt 
                WHERE zid = %s AND xordernum = %s
            """, [zid, transaction_id])
            
            # Insert updated items
            for item in items_data:
                # Calculate line amount if not provided
                qty = float(item.get('xqtyord', 0))
                rate = float(item.get('xrate', 0))
                line_amount = qty * rate
                
                cursor.execute("""
                    INSERT INTO opodt (
                        zid, xordernum, xrow, xitem, xdesc, xunitsel, 
                        xqtyord, xrate, xlineamt, xdttax
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    zid,
                    transaction_id,
                    item.get('xrow', 1),
                    item.get('xitem', ''),
                    item.get('xdesc', ''),
                    item.get('xunitsel', 'PCS'),
                    qty,
                    rate,
                    line_amount,
                    float(item.get('xdttax', 0))
                ])
            
            # Update total amount in header
            cursor.execute("""
                UPDATE opord 
                SET xtotamt = (
                    SELECT COALESCE(SUM(xlineamt), 0) 
                    FROM opodt 
                    WHERE zid = %s AND xordernum = %s
                )
                WHERE zid = %s AND xordernum = %s
            """, [zid, transaction_id, zid, transaction_id])
            
            return {'success': True, 'message': 'Items updated successfully'}
            
    except Exception as e:
        logger.error(f"Error updating transaction items: {str(e)}")
        return {
            'success': False,
            'message': f'Error updating items: {str(e)}'
        }