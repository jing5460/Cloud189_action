def hide_username(name: str) -> str:
    u_len = len(name)
    fill_len = int(u_len * 0.3) + 1
    b_index = int((u_len - fill_len) / 2)
    e_index = u_len - fill_len - b_index
    return name[:b_index] + "*" * fill_len + name[-e_index:]


def print_msg(msg: str = "", isFirstLine: bool = False):
    indent = " " * 4 if isFirstLine and msg != "" else ""
    print(indent + msg)
