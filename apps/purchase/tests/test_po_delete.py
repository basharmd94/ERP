from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch


class CursorStub:
    def __init__(self, po_exists=True, raise_on=None):
        self.po_exists = po_exists
        self.raise_on = raise_on or ''
        self.last_sql = ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.last_sql = sql
        if self.raise_on and self.raise_on in sql:
            raise Exception('Simulated DB error')

    def fetchone(self):
        if 'FROM poord' in self.last_sql:
            return ['PO123'] if self.po_exists else None
        return None

    def fetchall(self):
        if 'FROM pogrn' in self.last_sql:
            return [('GRN001', 'VOUCHER1')]
        return []


class PoDeleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        session = self.client.session
        session['current_zid'] = 1
        session.save()

    @patch('apps.purchase.views.po_delete.connection.cursor')
    def test_delete_success(self, mock_cursor):
        mock_cursor.return_value = CursorStub(po_exists=True)
        resp = self.client.post('/purchase/po-delete/PO123/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertIn('deleted_records', data)

    def test_method_not_allowed(self):
        resp = self.client.get('/purchase/po-delete/PO123/')
        self.assertEqual(resp.status_code, 405)

    def test_missing_zid(self):
        c = Client()
        c.force_login(self.user)
        resp = c.post('/purchase/po-delete/PO123/')
        self.assertEqual(resp.status_code, 401)

    @patch('apps.purchase.views.po_delete.connection.cursor')
    def test_po_not_found(self, mock_cursor):
        mock_cursor.return_value = CursorStub(po_exists=False)
        resp = self.client.post('/purchase/po-delete/PO999/')
        self.assertEqual(resp.status_code, 404)

    @patch('apps.purchase.views.po_delete.connection.cursor')
    def test_deletion_error_rollback(self, mock_cursor):
        mock_cursor.return_value = CursorStub(po_exists=True, raise_on='DELETE FROM poord')
        resp = self.client.post('/purchase/po-delete/POERR/')
        self.assertEqual(resp.status_code, 500)
        data = resp.json()
        self.assertFalse(data['success'])

