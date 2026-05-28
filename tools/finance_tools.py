def transfer_funds(amount, destination, approval_id=None):
    print(f"\n🔄 Executing transfer: ${amount:,.0f} -> {destination}")

    if amount >= 1000000:
        print("🚨 HIGH VALUE TRANSFER DETECTED")

    if approval_id:
        print(f"Approval ID: {approval_id}")

    result = {
        "status": "success",
        "amount": amount,
        "destination": destination
    }

    print("✅ Transfer completed")

    return result

print("✅ Finance tools ready")
