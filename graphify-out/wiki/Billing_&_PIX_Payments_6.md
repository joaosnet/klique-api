# Billing & PIX Payments

> 9 nodes · cohesion 0.22

## Key Concepts

- **MercadoPagoService** (6 connections) — `app/services/mercadopago.py`
- **.create_pix_payment()** (2 connections) — `app/services/mercadopago.py`
- **.get_payment_status()** (2 connections) — `app/services/mercadopago.py`
- **.verify_webhook_signature()** (2 connections) — `app/services/mercadopago.py`
- **.__init__()** (1 connections) — `app/services/mercadopago.py`
- **Consulta o status de um pagamento. Args: payment_id: ID do pagamento no Mercado…** (1 connections) — `app/services/mercadopago.py`
- **Valida a assinatura do webhook do Mercado Pago. Args: x_signature: Header…** (1 connections) — `app/services/mercadopago.py`
- **Serviço para integração com a API do Mercado Pago.** (1 connections) — `app/services/mercadopago.py`
- **Cria uma cobrança PIX no Mercado Pago. Args: amount: Valor em R$ (mínimo R$…** (1 connections) — `app/services/mercadopago.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `app/services/mercadopago.py`

## Audit Trail

- EXTRACTED: 8 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*