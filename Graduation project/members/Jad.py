def New_Box(length, width, height, weight, color=""):
    def maybe_num(x):
        try:
            if "." in x:
                return float(x)
            return int(x)
        except:
            return x.strip()

    return {
        "length": maybe_num(length),
        "width": maybe_num(width),
        "height": maybe_num(height),
        "weight": maybe_num(weight),
        "color": color.strip() if isinstance(color, str) else color,
    }


def Warehouse_Size(length, width, height):
    def maybe_num(x):
        try:
            if "." in x:
                return float(x)
            return int(x)
        except:
            return x.strip()

    return {
        "length": maybe_num(length),
        "width": maybe_num(width),
        "height": maybe_num(height),
    }
