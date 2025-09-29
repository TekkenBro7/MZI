
H_TABLE = [
    0xB1, 0x94, 0xBA, 0xC8, 0x0A, 0x08, 0xF5, 0x3B, 0x36, 0x6D, 0x00, 0x8E, 0x58, 0x4A, 0x5D, 0xE4,
    0x85, 0x04, 0xFA, 0x9D, 0x1B, 0xB6, 0xC7, 0xAC, 0x25, 0x2E, 0x72, 0xC2, 0x02, 0xFD, 0xCE, 0x0D,
    0x5B, 0xE3, 0xD6, 0x12, 0x17, 0xB9, 0x61, 0x81, 0xFE, 0x67, 0x86, 0xAD, 0x71, 0x6B, 0x89, 0x0B,
    0x5C, 0xB0, 0xC0, 0xFF, 0x33, 0xC3, 0x56, 0xB8, 0x35, 0xC4, 0x05, 0xAE, 0xD8, 0xE0, 0x7F, 0x99,
    0xE1, 0x2B, 0xDC, 0x1A, 0xE2, 0x82, 0x57, 0xEC, 0x70, 0x3F, 0xCC, 0xF0, 0x95, 0xEE, 0x8D, 0xF1,
    0xC1, 0xAB, 0x76, 0x38, 0x9F, 0xE6, 0x78, 0xCA, 0xF7, 0xC6, 0xF8, 0x60, 0xD5, 0xBB, 0x9C, 0x4F,
    0xF3, 0x3C, 0x65, 0x7B, 0x63, 0x7C, 0x30, 0x6A, 0xDD, 0x4E, 0xA7, 0x79, 0x9E, 0xB2, 0x3D, 0x31,
    0x3E, 0x98, 0xB5, 0x6E, 0x27, 0xD3, 0xBC, 0xCF, 0x59, 0x1E, 0x18, 0x1F, 0x4C, 0x5A, 0xB7, 0x93,
    0xE9, 0xDE, 0xE7, 0x2C, 0x8F, 0x0C, 0x0F, 0xA6, 0x2D, 0xDB, 0x49, 0xF4, 0x6F, 0x73, 0x96, 0x47,
    0x06, 0x07, 0x53, 0x16, 0xED, 0x24, 0x7A, 0x37, 0x39, 0xCB, 0xA3, 0x83, 0x03, 0xA9, 0x8B, 0xF6,
    0x92, 0xBD, 0x9B, 0x1C, 0xE5, 0xD1, 0x41, 0x01, 0x54, 0x45, 0xFB, 0xC9, 0x5E, 0x4D, 0x0E, 0xF2,
    0x68, 0x20, 0x80, 0xAA, 0x22, 0x7D, 0x64, 0x2F, 0x26, 0x87, 0xF9, 0x34, 0x90, 0x40, 0x55, 0x11,
    0xBE, 0x32, 0x97, 0x13, 0x43, 0xFC, 0x9A, 0x48, 0xA0, 0x2A, 0x88, 0x5F, 0x19, 0x4B, 0x09, 0xA1,
    0x7E, 0xCD, 0xA4, 0xD0, 0x15, 0x44, 0xAF, 0x8C, 0xA5, 0x84, 0x50, 0xBF, 0x66, 0xD2, 0xE8, 0x8A,
    0xA2, 0xD7, 0x46, 0x52, 0x42, 0xA8, 0xDF, 0xB3, 0x69, 0x74, 0xC5, 0x51, 0xEB, 0x23, 0x29, 0x21,
    0xD4, 0xEF, 0xD9, 0xB4, 0x3A, 0x62, 0x28, 0x75, 0x91, 0x14, 0x10, 0xEA, 0x77, 0x6C, 0xDA, 0x1D,
]

def add_zero_padding(data, n):
    padding_length = (n - len(data) % n) % n
    
    if padding_length > 0:
        padded_data = data + b'\x00' * padding_length
    else:
        padded_data = data
    return padded_data


def split_into_nbyte_blocks(data, n):
    padded_data = add_zero_padding(data, n)
    
    blocks = []
    for i in range(0, len(padded_data), n):
        block = padded_data[i:i+n]
        blocks.append(block)
    
    return blocks


def rotate_left(n, bits, shift):
    shift %= bits
    return ((n << shift) | (n >> (bits - shift))) & ((1 << bits) - 1)


def sum_mod(*args):
    return sum(args) & 0xFFFFFFFF


def G(u, r):
    u8 = [(u >> (24 - 8*i)) & 0xFF for i in range(4)]
    h8 = [H_TABLE[byte] for byte in u8]
    v = (h8[0] << 24) | (h8[1] << 16) | (h8[2] << 8) | h8[3]
    return rotate_left(v, 32, r)


def block_encrypt(block128, keys32):
    blocks32 = split_into_nbyte_blocks(block128, 4)
    a, b, c, d = list(map(lambda block32: int.from_bytes(block32), blocks32))
    
    K = lambda i: keys32[i % 8]
    for i in range(1, 9):
        b ^= G(sum_mod(a, K(7*i-7)), 5)
        c ^= G(sum_mod(d, K(7*i-6)), 21)
        a = sum_mod(a, -G(sum_mod(b, K(7*i-5)), 13))
        e = G(sum_mod(b, c, K(7*i-4)), 21) ^ i
        b = sum_mod(b, e)
        c = sum_mod(c, -e)
        d = sum_mod(d, G(sum_mod(c, K(7*i-3)), 13))
        b ^= G(sum_mod(a, K(7*i-2)), 21)
        c ^= G(sum_mod(d, K(7*i-1)), 5)
        a, b = b, a
        c, d = d, c
        b, c = c, b
    
    Y = b.to_bytes(4) + d.to_bytes(4) + a.to_bytes(4) + c.to_bytes(4)
    return Y


def block_decrypt(block128, keys32):
    blocks32 = split_into_nbyte_blocks(block128, 4)
    a, b, c, d = list(map(lambda block32: int.from_bytes(block32), blocks32))
    
    K = lambda i: keys32[i % 8]
    for i in range(8, 0, -1):
        b ^= G(sum_mod(a, K(7*i-1)), 5)
        c ^= G(sum_mod(d, K(7*i-2)), 21)
        a = sum_mod(a, -G(sum_mod(b, K(7*i-3)), 13))
        e = G(sum_mod(b, c, K(7*i-4)), 21) ^ i
        b = sum_mod(b, e)
        c = sum_mod(c, -e)
        d = sum_mod(d, G(sum_mod(c, K(7*i-5)), 13))
        b ^= G(sum_mod(a, K(7*i-6)), 21)
        c ^= G(sum_mod(d, K(7*i-7)), 5)
        a, b = b, a
        c, d = d, c
        a, d = d, a

    Y = c.to_bytes(4) + a.to_bytes(4) + d.to_bytes(4) + b.to_bytes(4)
    return Y


def belt_simple_replace(data, key256, mode):
    blocks = split_into_nbyte_blocks(data, 16)
    keys32 = split_into_nbyte_blocks(key256, 4)
    keys32 = list(map(lambda block: int.from_bytes(block), keys32))
    
    result_blocks = []
    if mode == 'encrypt':
        for block in blocks:
            encrypted_block = block_encrypt(block, keys32)
            result_blocks.append(encrypted_block)
    else:
        for block in blocks:
            decrypted_block = block_decrypt(block, keys32)
            result_blocks.append(decrypted_block)
    return b''.join(result_blocks)


def L_n(gamma, n):
    return gamma[:n]


def belt_feedback_gamma(data, key256, S, mode='encrypt'):
    keys32 = split_into_nbyte_blocks(key256, 4)
    keys32 = list(map(lambda block: int.from_bytes(block), keys32))
    
    blocks = []
    for i in range(0, len(data), 16):
        block = data[i:i+16]
        blocks.append(block)
    
    result_blocks = []
    feedback = S
    for i, block in enumerate(blocks):
        gamma_full = block_encrypt(feedback, keys32)
        gamma = L_n(gamma_full, len(block))
        
        result_block = bytes(x ^ y for x, y in zip(block, gamma))
        result_blocks.append(result_block)
        
        if mode == 'encrypt':
            feedback = result_block
        else:
            feedback = block 
    return b''.join(result_blocks)