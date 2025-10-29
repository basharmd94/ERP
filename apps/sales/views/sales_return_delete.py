

from django.http import JsonResponse
from django.db import transaction, connection
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
@transaction.atomic
def sales_return_delete(request, transaction_id):
    """
    Delete sales return transaction and all related records.
    Handles both posted (GL) and unposted transactions.
    """
    try:
        # Get session ZID
        session_zid = request.session.get('current_zid')
        if not session_zid:
            return JsonResponse({
                'success': False,
                'message': 'Session expired. Please login again.'
            }, status=401)

        logger.info(f"Deleting sales return transaction: {transaction_id} for ZID: {session_zid}")

        with connection.cursor() as cursor:
            # First, check if transaction exists
            cursor.execute("""
                SELECT ximtmptrn, xglref
                FROM imtemptrn
                WHERE zid = %s AND ximtmptrn = %s
            """, [session_zid, transaction_id])

            transaction_data = cursor.fetchone()
            if not transaction_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Sales return transaction not found.'
                }, status=404)

            ximtmptrn, xglref = transaction_data
            logger.info(f"Found transaction: {ximtmptrn}, GL Ref: {xglref}")

            # Delete from GL tables if posted (xglref exists)
            if xglref:
                logger.info(f"Deleting GL records for voucher: {xglref}")

                # Delete from gldetail
                cursor.execute("""
                    DELETE FROM gldetail
                    WHERE zid = %s AND xvoucher = %s
                """, [session_zid, xglref])
                gldetail_deleted = cursor.rowcount
                logger.info(f"Deleted {gldetail_deleted} records from gldetail")

                # Delete from glheader
                cursor.execute("""
                    DELETE FROM glheader
                    WHERE zid = %s AND xvoucher = %s
                """, [session_zid, xglref])
                glheader_deleted = cursor.rowcount
                logger.info(f"Deleted {glheader_deleted} records from glheader")

            # Delete from imtrn (inventory transactions)
            cursor.execute("""
                DELETE FROM imtrn
                WHERE zid = %s AND xdocnum = %s
            """, [session_zid, transaction_id])
            imtrn_deleted = cursor.rowcount
            logger.info(f"Deleted {imtrn_deleted} records from imtrn")

            # Delete from imtemptdt (transaction details)
            cursor.execute("""
                DELETE FROM imtemptdt
                WHERE zid = %s AND ximtmptrn = %s
            """, [session_zid, transaction_id])
            imtemptdt_deleted = cursor.rowcount
            logger.info(f"Deleted {imtemptdt_deleted} records from imtemptdt")

            # Finally, delete from imtemptrn (main transaction)
            cursor.execute("""
                DELETE FROM imtemptrn
                WHERE zid = %s AND ximtmptrn = %s
            """, [session_zid, transaction_id])
            imtemptrn_deleted = cursor.rowcount
            logger.info(f"Deleted {imtemptrn_deleted} records from imtemptrn")

            if imtemptrn_deleted == 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to delete sales return transaction.'
                }, status=500)

        logger.info(f"Successfully deleted sales return transaction: {transaction_id}")

        return JsonResponse({
            'success': True,
            'message': 'Sales return transaction deleted successfully.',
            'deleted_records': {
                'imtemptrn': imtemptrn_deleted,
                'imtemptdt': imtemptdt_deleted,
                'imtrn': imtrn_deleted,
                'glheader': glheader_deleted if xglref else 0,
                'gldetail': gldetail_deleted if xglref else 0
            }
        })

    except Exception as e:
        logger.error(f"Error deleting sales return transaction {transaction_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error deleting transaction: {str(e)}'
        }, status=500)
