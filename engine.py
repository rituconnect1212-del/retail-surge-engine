def calculate_surge_and_depletion(current_stock, safety_stock, orders_per_min, base_price, lead_time_min):
    velocity = max(orders_per_min, 0.1)
    time_to_exhaust_min = current_stock / velocity
    
    if time_to_exhaust_min < lead_time_min or current_stock <= safety_stock:
        risk_level = "CRITICAL"
        scarcity_ratio = max(0.0, (lead_time_min - time_to_exhaust_min) / lead_time_min)
        surge_multiplier = round(1.0 + (0.5 * scarcity_ratio), 2)
    elif time_to_exhaust_min < (lead_time_min * 1.5):
        risk_level = "MODERATE"
        surge_multiplier = 1.15
    else:
        risk_level = "NORMAL"
        surge_multiplier = 1.0

    dynamic_price = round(base_price * surge_multiplier, 2)
    arbitrage_margin = round(dynamic_price - base_price, 2)

    return {
        "time_to_exhaust_min": round(time_to_exhaust_min, 1),
        "risk_level": risk_level,
        "surge_multiplier": surge_multiplier,
        "dynamic_price": dynamic_price,
        "arbitrage_margin": arbitrage_margin
    }
