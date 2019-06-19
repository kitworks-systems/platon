from textwrap import dedent
from unittest import TestCase


from unittest.mock import patch
import requests

from platon import Platon, Api
from platon.constants import SUPPORTED_LANGUAGES, TransactionType, SUPPORTED_PAYMENT, SUPPORTED_CURRENCY
from platon.generators import Form
from platon.params import ParamValidationError, Params, ParamRequired, FrozenParams
from platon.utils import generate_signature, strrev


class UtilsTestCase(TestCase):
    def test_generate_signature(self):
        signature = generate_signature([1, '<test>', [1, 'val"', 2.2]])
        self.assertEqual(signature, '58e87bbb04ee6c629bcdde18cd62fac5')
        signature = generate_signature([1, '<testtest>', (1, 'val"', 2.2)])
        self.assertEqual(signature, 'cf3dfd3155a58873e335fff98d4959a6')

    def test_strrev(self):
        reversed_string = strrev("123")
        self.assertEqual(reversed_string, '321')
        self.assertRaises(TypeError, strrev, 123)
        self.assertRaises(TypeError, strrev, [])
        self.assertRaises(TypeError, strrev, {})


class ParamsTestCase(TestCase):
    def test_transaction_type_validation(self):
        self.assertRaises(ParamValidationError, Params, transactionType='')
        self.assertRaises(ParamValidationError, Params, transactionType='test')
        self.assertEqual(Params(transactionType='PURCHASE')['transactionType'], 'PURCHASE')
        self.assertEqual(Params(transactionType=TransactionType.PURCHASE)['transactionType'], 'PURCHASE')

    def test_required_field_validation(self):
        self.assertRaises(ParamValidationError, Params, key='')
        self.assertEqual(Params(key='test')['key'], 'test')

    def test_lang_validation(self):
        for lang in ['', 'test', 'auto', 'en', 'ru', 'ua', 'uk', 'UA']:
            self.assertRaises(ParamValidationError, Params, lang=lang)
        for lang in SUPPORTED_LANGUAGES:
            self.assertEqual(Params(lang=lang)['lang'], lang)

    def test_payment_validation(self):
        for payment in ['', 'cc', 'cC', 'cct', 'fr', 'FR', 'ccT', 'rf']:
            self.assertRaises(ParamValidationError, Params, payment=payment)
        for payment in SUPPORTED_PAYMENT:
            self.assertEqual(Params(payment=payment)['payment'], payment)

    def test_currency_validation(self):
        for currency in ['', 'cc', 'cC', 'cct', 'fr', 'FR', 'ccT', 'rf']:
            self.assertRaises(ParamValidationError, Params, currency=currency)
        for currency in SUPPORTED_CURRENCY:
            self.assertEqual(Params(currency=currency)['currency'], currency)

    def test_signature(self):
        params = Params()
        self.assertRaises(ParamRequired, params._generate_signature, 'password')
        params['transactionType'] = TransactionType.PURCHASE
        self.assertRaises(ParamRequired, params._generate_signature, 'password')
        params.update(key='acc', data='{}', url='test', payment='CC')
        signature = params._generate_signature('password')
        self.assertEqual(signature, '1a1a62481a2f4754b027c4e7a619c16f')

    def test_prepare(self):
        params = Params(transactionType=TransactionType.PURCHASE, key='acc', data='{}')
        self.assertRaises(ParamRequired, params.prepare, 'password')
        params['url'] = 'test'
        self.assertRaises(ParamRequired, params.prepare, 'password')
        params['payment'] = 'CC'
        self.assertIsNone(params.prepare('password'))
        data_params = Params(transactionType=TransactionType.PURCHASE, key='acc', amount='12.00', description="YOLO",
                             currency="UAH", url='test', payment='CC')
        self.assertIsNone(data_params.prepare('password'))


class FrozenParamsTestCase(TestCase):
    def test_init(self):
        self.assertRaises(ParamRequired, FrozenParams, 'acc', 'key', TransactionType.CREATE_INVOICE, {})
        params = FrozenParams('acc', 'key', TransactionType.CREATE_INVOICE, dict(
            order='4221', amount='12.00', action='create', description='YOLO'))
        self.assertEqual(params['sign'], '12e3f227b59c8470c440e02e12b4305b')

    def test_immutability(self):
        params = FrozenParams('acc', 'password', TransactionType.CREATE_INVOICE, dict(
            order='4221', amount='12.00', action='create', description='YOLO'))
        with self.assertRaises(NotImplementedError):
            params['test'] = 1
        with self.assertRaises(NotImplementedError):
            params.update(test=1)
        with self.assertRaises(NotImplementedError):
            del params['test']
        with self.assertRaises(NotImplementedError):
            params.pop('action')


class ConfirmParamsTestCase(TestCase):
    def test_init(self):
        params = FrozenParams('acc', 'password', TransactionType.CONFIRM_PURCHASE, dict(
            email='test@test.test', order='1', card='555555****5555', sign='test'))
        self.assertEqual(params['sign'], 'afa0f44c3adb9c9d06ebec3d027c0797')


class FormTestCase(TestCase):
    def test_rendering(self):
        form = Form(
            'acc', 'password', dict(order='4221', amount='12.00', currency='UAH', payment='CC',
                                    description="Test Order", url='example.com',)
        )
        self.assertEqual(form.render(), dedent('''\
            <form method="post" action="https://secure.platononline.com/payment/auth" accept-charset="utf-8">
                <input type="hidden" name="key" value="acc" />
                <input type="hidden" name="order" value="4221" />
                <input type="hidden" name="payment" value="CC" />
                <input type="hidden" name="url" value="example.com" />
                <input type="hidden" name="data" value="{&quot;amount&quot;: &quot;12.00&quot;, &quot;currency&quot;: &quot;UAH&quot;, &quot;description&quot;: &quot;Test Order&quot;}" />
                <input type="hidden" name="sign" value="537a7ac3505c65d6c65ba14283b07648" />
                <input type="submit" value="Submit purchase form">
            </form>'''))


@patch.object(requests, 'post')
class ApiTestCase(TestCase):
    def setUp(self):
        self.api = Api('acc', 'key')

    def test_query(self, post_mock):
        self.assertRaises(ParamRequired, self.api._query, TransactionType.CREATE_INVOICE, {})
        post_mock.assert_not_called()

        self.api._query(TransactionType.CREATE_INVOICE, dict(
            order='4221', amount='12.00', action='create', description='YOLO'))
        post_mock.assert_called_once()

    def test_shortcuts(self, post_mock):
        self.api.create_invoice(dict(order='4221', amount='12.00', action='create', description='YOLO'))
        post_mock.assert_called_once()
        self.assertEqual(post_mock.call_args[1]['json']['transactionType'], TransactionType.CREATE_INVOICE.value)


class PlatonTestCase(TestCase):
    def setUp(self):
        self.platon = Platon('acc', 'key')
