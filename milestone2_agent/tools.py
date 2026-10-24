"""
tools.py - Defines the executable tools and their schemas for the AI Agent.
"""

from typing import Dict, Any


# Mock in-memory database
ORDER_DATABASE = {
    "ORD-101": {
        "order_id": "ORD-101",
        "customer": "Aarav Sharma",
        "status": "Shipped",
        "carrier": "BlueDart",
        "tracking_number": "BD-8892110",
        "estimated_delivery": "2026-10-26"
    },
    "ORD-102": {
        "order_id": "ORD-102",
        "customer": "Priya Patel",
        "status": "Processing",
        "carrier": "Delhivery",
        "tracking_number": "Pending",
        "estimated_delivery": "2026-10-29"
    }
}

INVENTORY_DATABASE = {
    "SKU-MACBOOK": {
        "item": "MacBook Pro M3 14-inch",
        "in_stock": 14,
        "price_inr": 169900,
        "warehouse_location": "Bangalore"
    },
    "SKU-KEYBOARD": {
        "item": "Keychron K2 Mechanical Keyboard",
        "in_stock": 0,
        "price_inr": 8499,
        "restock_date": "2026-11-05"
    }
}


def get_order_status(order_id: str) -> Dict[str, Any]:
    """
    Look up the live fulfillment status and tracking info for a customer order.
    Returns structured data or an error if the order does not exist.
    """
    clean_id = order_id.strip().upper()
    if clean_id in ORDER_DATABASE:
        return {"success": True, "data": ORDER_DATABASE[clean_id]}
    return {
        "success": False,
        "error": f"Order ID '{order_id}' was not found in the order management database."
    }


def check_product_inventory(sku: str) -> Dict[str, Any]:
    """
    Check warehouse inventory levels, pricing, and availability for a product SKU.
    """
    clean_sku = sku.strip().upper()
    if clean_sku in INVENTORY_DATABASE:
        return {"success": True, "data": INVENTORY_DATABASE[clean_sku]}
    return {
        "success": False,
        "error": f"Product SKU '{sku}' was not found in the inventory system."
    }


def calculate_shipping_cost(weight_kg: float, distance_km: float) -> Dict[str, Any]:
    """
    Calculate shipping fees based on package weight (kg) and distance (km).
    """
    if weight_kg <= 0 or distance_km <= 0:
        return {"success": False, "error": "Weight and distance must both be positive numbers."}
    
    base_rate = 50.0  # INR
    weight_charge = weight_kg * 25.0
    distance_charge = (distance_km / 100.0) * 15.0
    total_cost = round(base_rate + weight_charge + distance_charge, 2)

    return {
        "success": True,
        "data": {
            "weight_kg": weight_kg,
            "distance_km": distance_km,
            "shipping_cost_inr": total_cost,
            "currency": "INR"
        }
    }


# Tool Registry mapping names to functions and tool documentation
TOOL_REGISTRY = {
    "get_order_status": {
        "func": get_order_status,
        "description": "Fetch order fulfillment status and tracking information by Order ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "e.g., ORD-101"}
            },
            "required": ["order_id"]
        }
    },
    "check_product_inventory": {
        "func": check_product_inventory,
        "description": "Check stock availability and price for a given product SKU.",
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {"type": "string", "description": "e.g., SKU-MACBOOK or SKU-KEYBOARD"}
            },
            "required": ["sku"]
        }
    },
    "calculate_shipping_cost": {
        "func": calculate_shipping_cost,
        "description": "Calculate logistics delivery fee based on package weight and distance.",
        "parameters": {
            "type": "object",
            "properties": {
                "weight_kg": {"type": "number", "description": "Package weight in kilograms"},
                "distance_km": {"type": "number", "description": "Delivery distance in kilometers"}
            },
            "required": ["weight_kg", "distance_km"]
        }
    }
}
