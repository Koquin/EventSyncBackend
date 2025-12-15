def debug_print(file: str, method: str, message: str, **kwargs):
    """Print debug information"""
    vars_str = ", ".join([f"{k}: {v}" for k, v in kwargs.items()])
    if vars_str:
        print(f"[DEBUG] In {file}, method {method}, {message} ({vars_str})")
    else:
        print(f"[DEBUG] In {file}, method {method}, {message}")
