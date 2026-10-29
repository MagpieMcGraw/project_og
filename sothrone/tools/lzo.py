"""LZO1X decompressor (standard format), returns (output, bytes consumed)."""


def decompress(src, start=0, limit=None):
    ip = start
    out = bytearray()

    def copy_match(dist, length):
        pos = len(out) - dist
        if pos < 0:
            raise ValueError(f"match before start: dist {dist} at out {len(out)} ip {ip}")
        for k in range(length):
            out.append(out[pos + k])

    def literal_run(t):
        nonlocal ip
        out.extend(src[ip:ip + t])
        ip += t

    def extended(t, base):
        nonlocal ip
        if t == 0:
            while src[ip] == 0:
                t += 255
                ip += 1
            t += base + src[ip]
            ip += 1
        return t

    state = 0  # literals copied after the last match (0, 1-3, or 4 = long run)
    b = src[ip]
    if b > 17:
        ip += 1
        literal_run(b - 17)
        state = 4 if b - 17 >= 4 else b - 17
    while True:
        if limit is not None and len(out) > limit:
            raise ValueError("over limit")
        b = src[ip]
        ip += 1
        if b < 16:
            if state == 0:
                t = extended(b, 15)
                literal_run(t + 3)
                state = 4
                continue
            if state == 4:
                dist = 1 + 0x800 + (b >> 2) + (src[ip] << 2)
                ip += 1
                copy_match(dist, 3)
            else:
                dist = 1 + (b >> 2) + (src[ip] << 2)
                ip += 1
                copy_match(dist, 2)
            trailing = b & 3
        elif b >= 64:
            dist = 1 + ((b >> 2) & 7) + (src[ip] << 3)
            ip += 1
            copy_match(dist, (b >> 5) + 1)
            trailing = b & 3
        elif b >= 32:
            t = extended(b & 31, 31)
            d = src[ip] | (src[ip + 1] << 8)
            ip += 2
            copy_match(1 + (d >> 2), t + 2)
            trailing = d & 3
        else:
            t = extended(b & 7, 7)
            d = src[ip] | (src[ip + 1] << 8)
            ip += 2
            dist = ((b & 8) << 11) + (d >> 2)
            if dist == 0:
                return bytes(out), ip - start
            copy_match(dist + 0x4000, t + 2)
            trailing = d & 3
        literal_run(trailing)
        state = trailing
