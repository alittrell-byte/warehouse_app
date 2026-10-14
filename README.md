## Running test migrations
- run this when a model is changed or added - `docker compose run --rm migrator alembic revision --autogenerate -m "description"`

- then do a regular `docker compose up`

## What is this?
This app automates and cleans up the handoff of product data between a PO, receipt, and an invoice. 

### Data flow
1. Must exist
 - Vendor
 - Product
 - ProductVendor - the vendor item number may be different than the manufacturer id
2. PurchaseOrder
 - A purchase order is created and sent to a vendor for processing.
 - It would be best practice to have an existing PO before creating an invoice. In the event of a double shipment of a PO, a secondary PO must be created in order to receive the additional items.
 - Line Items containing items and quantities must be added to the PO and the PO sent to a Vendor before an Invoice or packing slip would be received.
3. Packing Slip with Lines
 - This is the fulfillment of an invoice. This could align with one or more POs or invoices
4. Receipt
 - A receiving associate would compare physically received items against the packing slip quantities, verifying item number and quantities.
 - A threshold of qty variance may be adjusted (default 2%) to auto reconcile or not. 
 - Variances beyond 2% difference will need manual approval by a different associate to verify the accuracy of the receipt and determine the end result of the discrepant product.
5. An invoice with lines is created against a specific PO or POs.
 - approved receipts will auto reconcile to the invoice. 
 - Price variances beyond 2% will be flagged for review.

*Work in progress*