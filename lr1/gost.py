class GOST28147_89:
    S_BOX = [
        [4, 10, 9, 2, 13, 8, 0, 14, 6, 11, 1, 12, 7, 15, 5, 3],
        [14, 11, 4, 12, 6, 13, 15, 10, 2, 3, 8, 1, 0, 7, 5, 9],
        [5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11],
        [7, 13, 10, 1, 0, 8, 9, 15, 14, 4, 6, 12, 11, 2, 5, 3],
        [6, 12, 7, 1, 5, 15, 13, 8, 4, 10, 9, 14, 0, 3, 11, 2],
        [4, 11, 10, 0, 7, 2, 1, 13, 3, 6, 8, 5, 9, 12, 15, 14],
        [13, 11, 4, 1, 3, 15, 5, 9, 0, 10, 14, 7, 6, 8, 2, 12],
        [1, 15, 13, 0, 5, 7, 10, 4, 9, 2, 3, 14, 6, 11, 8, 12]
    ]
    
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Ключ должен быть 256 бит (32 байта)")
        
        self.subkeys = [int.from_bytes(key[i:i+4], 'little') for i in range(0, 32, 4)]
    
    def gost_f(self, data: int, subkey: int) -> int:
        temp = (data + subkey) & 0xFFFFFFFF
        
        result = 0
        for i in range(8):
            s_box_input = (temp >> (4 * i)) & 0xF
            s_box_output = self.S_BOX[i][s_box_input]
            result |= s_box_output << (4 * i)
        
        return ((result << 11) | (result >> (32 - 11))) & 0xFFFFFFFF
    
    def _encrypt_block(self, block: bytes) -> bytes:
        if len(block) != 8:
            block = block.ljust(8, b'\x00')
        
        left = int.from_bytes(block[:4], 'little')
        right = int.from_bytes(block[4:], 'little')
        
        for i in range(32):
            if i < 25:
                subkey = self.subkeys[i % 8]
            else:
                subkey = self.subkeys[8 - (i % 8)]
            
            f_result = self.gost_f(right, subkey)
            new_right = left ^ f_result
            left, right = right, new_right
        
        encrypted = left.to_bytes(4, 'little') + right.to_bytes(4, 'little')
        return encrypted
    
    def _decrypt_block(self, block: bytes) -> bytes:
        if len(block) != 8:
            block = block.ljust(8, b'\x00')
        
        left = int.from_bytes(block[:4], 'little')
        right = int.from_bytes(block[4:], 'little')
        
        for i in range(31, -1, -1):
            if i < 25:
                subkey = self.subkeys[i % 8]
            else:
                subkey = self.subkeys[8 - (i % 8)]
            
            f_result = self.gost_f(left, subkey)
            new_left = right ^ f_result
            right, left = left, new_left
        
        decrypted = left.to_bytes(4, 'little') + right.to_bytes(4, 'little')
        return decrypted
    
    def encrypt_ecb(self, data: bytes) -> bytes:
        padding = 8 - (len(data) % 8)
        if padding != 8:
            data += bytes([padding] * padding)
        else:
            data += bytes([8] * 8)
        
        encrypted_blocks = []
        for i in range(0, len(data), 8):
            block = data[i:i+8]
            encrypted_block = self._encrypt_block(block)
            encrypted_blocks.append(encrypted_block)
        
        return b''.join(encrypted_blocks)
    
    def decrypt_ecb(self, data: bytes) -> bytes:
        decrypted_blocks = []
        for i in range(0, len(data), 8):
            block = data[i:i+8]
            decrypted_block = self._decrypt_block(block)
            decrypted_blocks.append(decrypted_block)
        
        result = b''.join(decrypted_blocks)
        padding = result[-1]
        if padding <= 8:
            result = result[:-padding]
        
        return result
