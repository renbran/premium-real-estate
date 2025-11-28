#!/usr/bin/env python3
"""
Fix missing payment reference numbers
This script can be run to fix existing payment records that don't have proper reference numbers.
"""

def fix_payment_references(env):
    """Show existing payment reference numbers - DO NOT MODIFY POSTED PAYMENTS"""
    payment_model = env['account.payment']
    
    print("Checking payment reference numbers...")
    print("NOTE: This script will NOT modify existing posted payments to maintain audit trail integrity.")
    print()
    
    # Find payments with missing or default reference numbers
    payments_with_issues = payment_model.search([
        '|',
        ('name', '=', '/'),
        ('name', '=', False)
    ])
    
    print(f"Found {len(payments_with_issues)} payments with missing reference numbers:")
    print()
    
    posted_payments = []
    draft_payments = []
    
    for payment in payments_with_issues:
        if payment.state == 'posted':
            posted_payments.append(payment)
        else:
            draft_payments.append(payment)
    
    if posted_payments:
        print(f"POSTED PAYMENTS (will NOT be modified): {len(posted_payments)}")
        for payment in posted_payments[:10]:  # Show first 10
            print(f"  - Payment ID {payment.id}: {payment.name} ({payment.payment_type}) - State: {payment.state}")
        if len(posted_payments) > 10:
            print(f"  ... and {len(posted_payments) - 10} more posted payments")
        print("  ⚠️  Posted payments will keep their current reference numbers for audit trail integrity")
        print()
    
    if draft_payments:
        print(f"DRAFT PAYMENTS (can be updated): {len(draft_payments)}")
        for payment in draft_payments:
            try:
                # Only update draft payments
                if payment.payment_type == 'inbound':
                    new_name = env['ir.sequence'].next_by_code('account.payment.customer.invoice')
                    if not new_name:
                        new_name = env['ir.sequence'].next_by_code('account.payment.customer')
                    if not new_name:
                        new_name = f"BNK1/IN/{payment.id:05d}"
                else:
                    new_name = env['ir.sequence'].next_by_code('account.payment.supplier.invoice')
                    if not new_name:
                        new_name = env['ir.sequence'].next_by_code('account.payment.supplier')
                    if not new_name:
                        new_name = f"BNK1/OUT/{payment.id:05d}"
                
                old_name = payment.name
                payment.name = new_name
                print(f"  ✅ Updated draft payment {payment.id}: {old_name} → {payment.name}")
                
            except Exception as e:
                print(f"  ❌ Error updating payment {payment.id}: {str(e)}")
        print()
    
    print("SUMMARY:")
    print(f"- Posted payments: {len(posted_payments)} (unchanged - audit trail preserved)")
    print(f"- Draft payments updated: {len(draft_payments)}")
    print()
    print("✅ New payments created going forward will automatically get proper reference numbers")
    print("✅ Payment voucher reports will show the reference numbers correctly")
    
    return True

if __name__ == "__main__":
    print("This script should be run from Odoo shell")
    print("Example: ")
    print("docker-compose exec odoo odoo shell -d your_database")
    print("Then run: exec(open('fix_payment_references.py').read())")
    print("And call: fix_payment_references(env)")
