"""
Input validation for trading operations
"""

import re
import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_symbol(symbol):
    """Validate trading symbol format"""
    if not symbol:
        raise ValidationError("Symbol cannot be empty")

    if not isinstance(symbol, str):
        raise ValidationError("Symbol must be a string")

    symbol = symbol.upper()

    # Basic symbol validation (e.g., BTCUSDT, ETHUSDT)
    if not re.match(r'^[A-Z]+$', symbol):
        raise ValidationError("Symbol must contain only uppercase letters")

    if len(symbol) < 6 or len(symbol) > 20:
        raise ValidationError("Symbol length must be between 6 and 20 characters")

    logger.info(f"Symbol validation passed: {symbol}")
    return symbol

def validate_quantity(quantity):
    """Validate order quantity"""
    if quantity is None:
        raise ValidationError("Quantity cannot be None")

    try:
        qty = Decimal(str(quantity))
    except (InvalidOperation, ValueError):
        raise ValidationError("Quantity must be a valid number")

    if qty <= 0:
        raise ValidationError("Quantity must be positive")

    if qty.as_tuple().exponent < -8:
        raise ValidationError("Quantity precision too high (max 8 decimal places)")

    logger.info(f"Quantity validation passed: {qty}")
    return float(qty)

def validate_price(price):
    """Validate order price"""
    if price is None:
        raise ValidationError("Price cannot be None")

    try:
        prc = Decimal(str(price))
    except (InvalidOperation, ValueError):
        raise ValidationError("Price must be a valid number")

    if prc <= 0:
        raise ValidationError("Price must be positive")

    if prc.as_tuple().exponent < -8:
        raise ValidationError("Price precision too high (max 8 decimal places)")

    logger.info(f"Price validation passed: {prc}")
    return float(prc)

def validate_order_type(order_type):
    """Validate order type"""
    valid_types = ['MARKET', 'LIMIT', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET']

    if not isinstance(order_type, str):
        raise ValidationError("Order type must be a string")

    order_type_upper = order_type.upper()
    if order_type_upper not in valid_types:
        raise ValidationError(f"Invalid order type. Must be one of: {', '.join(valid_types)}")

    logger.info(f"Order type validation passed: {order_type_upper}")
    return order_type_upper

def validate_side(side):
    """Validate order side (BUY/SELL)"""
    valid_sides = ['BUY', 'SELL']

    if not isinstance(side, str):
        raise ValidationError("Side must be a string")

    side_upper = side.upper()
    if side_upper not in valid_sides:
        raise ValidationError(f"Invalid side. Must be one of: {', '.join(valid_sides)}")

    logger.info(f"Side validation passed: {side_upper}")
    return side_upper

def validate_order_params(symbol, side, order_type, quantity=None, price=None):
    """Validate all order parameters"""
    errors = []

    try:
        symbol = validate_symbol(symbol)
    except ValidationError as e:
        errors.append(str(e))

    try:
        side = validate_side(side)
    except ValidationError as e:
        errors.append(str(e))

    try:
        order_type = validate_order_type(order_type)
    except ValidationError as e:
        errors.append(str(e))

    try:
        quantity = validate_quantity(quantity) if quantity is not None else None
    except ValidationError as e:
        errors.append(str(e))

    # Price is required for LIMIT orders
    if order_type == 'LIMIT':
        try:
            price = validate_price(price) if price is not None else None
            if price is None:
                errors.append("Price is required for LIMIT orders")
        except ValidationError as e:
            errors.append(str(e))

    if errors:
        raise ValidationError("; ".join(errors))

    return {
        'symbol': symbol,
        'side': side,
        'type': order_type,
        'quantity': quantity,
        'price': price
    }
