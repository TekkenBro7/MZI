from PIL import Image
import numpy as np
import os
from constants import DCT_BLOCK_SIZE, BIT_TARGET_COEFF, JPEG_QUANTIZATION_LUMINANCE, JPEG_QUANTIZATION_CHROMINANCE, DCT_MATRIX


def dct_forward(data_block):
    return DCT_MATRIX @ data_block @ DCT_MATRIX.T


def dct_inverse(coeffs):
    return DCT_MATRIX.T @ coeffs @ DCT_MATRIX


def text_to_bitstream(text):
    encoded_bytes = text.encode("utf-8")
    length_prefix = f"{len(encoded_bytes):032b}"
    byte_bits = [f"{byte:08b}" for byte in encoded_bytes]
    return length_prefix + "".join(byte_bits)


def bitstream_to_text(bitstring):
    if len(bitstring) < 32:
        return ""
    
    length_bits = bitstring[:32]
    data_length = int(length_bits, 2)
    data_bits = bitstring[32:32 + data_length * 8]
    
    byte_list = []
    for i in range(0, len(data_bits), 8):
        byte_bits = data_bits[i:i + 8]
        if len(byte_bits) == 8:
            byte_list.append(int(byte_bits, 2))
    
    try:
        return bytes(byte_list).decode("utf-8")
    except UnicodeDecodeError:
        return "[Ошибка декодирования]"


def modify_lsb_coefficient(coeff_value, bit):
    return ((coeff_value >> 1) << 1) | bit


def extract_lsb_coefficient(coeff_value):
    return coeff_value & 1


def make_zigzag_map(n=8):
    result = []
    for s in range(2 * n - 1):          
        if s % 2 == 0:
            x = min(s, n - 1)
            y = s - x
            while x >= 0 and y < n:
                result.append((x, y)) 
                x -= 1
                y += 1
        else:
            y = min(s, n - 1)
            x = s - y
            while y >= 0 and x < n:
                result.append((x, y)) 
                y -= 1
                x += 1
    return result   


def write_jpeg_with_custom_qtable(rgb_image, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    zigzag_pattern = make_zigzag_map(8)
    luminance_table = [int(JPEG_QUANTIZATION_LUMINANCE[i, j]) for i, j in zigzag_pattern]
    chrominance_table = [int(JPEG_QUANTIZATION_CHROMINANCE[i, j]) for i, j in zigzag_pattern]
    
    rgb_image.save(
        path, 
        "JPEG", 
        qtables=[luminance_table, chrominance_table], 
        subsampling=0, 
        quality=100
    )


def extend_block_to_8x8(block, target_size = DCT_BLOCK_SIZE):
    if block.shape == (target_size, target_size):
        return block
    
    padded_block = np.zeros((target_size, target_size), dtype=block.dtype)
    h, w = block.shape
    
    padded_block[:h, :w] = block
    
    if h < target_size:
        for i in range(h, target_size):
            padded_block[i, :w] = block[-1, :]  
    
    if w < target_size:
        for j in range(w, target_size):
            padded_block[:h, j] = block[:, -1]
    
    if h < target_size and w < target_size:
        padded_block[h:, w:] = block[-1, -1]
    
    return padded_block


def hide_data_in_image(original_image, bitstream):
    ycbcr_image = original_image.convert("YCbCr")
    image_array = np.array(ycbcr_image).astype(np.float64)
    luminance_channel = image_array[:, :, 0]
    
    height, width = luminance_channel.shape
    
    blocks_vertical = (height + DCT_BLOCK_SIZE - 1) // DCT_BLOCK_SIZE
    blocks_horizontal = (width + DCT_BLOCK_SIZE - 1) // DCT_BLOCK_SIZE
    total_blocks = blocks_vertical * blocks_horizontal
    
    if len(bitstream) > total_blocks:
        raise ValueError(f"Требуется блоков: {len(bitstream)}, доступно: {total_blocks}")
    
    processed_channel = luminance_channel.copy()
    u_coord, v_coord = BIT_TARGET_COEFF
    
    current_bit_index = 0
    
    for block_y in range(0, height, DCT_BLOCK_SIZE):
        for block_x in range(0, width, DCT_BLOCK_SIZE):
            block_end_y = min(block_y + DCT_BLOCK_SIZE, height)
            block_end_x = min(block_x + DCT_BLOCK_SIZE, width)
            
            block_region = luminance_channel[block_y:block_end_y, block_x:block_end_x]
            
            padded_block = extend_block_to_8x8(block_region)
            
            centered_block = padded_block - 128.0
            dct = dct_forward(centered_block)
            quantized_coefficients = np.rint(dct / JPEG_QUANTIZATION_LUMINANCE).astype(np.int32)
            
            if current_bit_index < len(bitstream):
                bit_value = int(bitstream[current_bit_index])
                modified_coeff = modify_lsb_coefficient(
                    int(quantized_coefficients[u_coord, v_coord]), 
                    bit_value
                )
                quantized_coefficients[u_coord, v_coord] = modified_coeff
                current_bit_index += 1
            
            reconstructed_dct = (quantized_coefficients * JPEG_QUANTIZATION_LUMINANCE).astype(np.float64)
            reconstructed_block = dct_inverse(reconstructed_dct) + 128.0
            
            block_height = block_end_y - block_y
            block_width = block_end_x - block_x
            processed_channel[block_y:block_end_y, block_x:block_end_x] = reconstructed_block[:block_height, :block_width]
    
    final_luminance = np.clip(np.rint(processed_channel), 0, 255).astype(np.uint8)
    image_array[:, :, 0] = final_luminance
    
    output_ycbcr = Image.fromarray(image_array.astype(np.uint8), mode="YCbCr")
    return output_ycbcr.convert("RGB")


def read_bits_from_image(stego_image, bits_needed):
    ycbcr_image = stego_image.convert("YCbCr")
    image_array = np.array(ycbcr_image).astype(np.float64)
    luminance_channel = image_array[:, :, 0]
    
    height, width = luminance_channel.shape
    u_coord, v_coord = BIT_TARGET_COEFF
    extracted_bits = []
    
    for block_y in range(0, height, DCT_BLOCK_SIZE):
        for block_x in range(0, width, DCT_BLOCK_SIZE):
            if len(extracted_bits) >= bits_needed:
                break
            
            block_end_y = min(block_y + DCT_BLOCK_SIZE, height)
            block_end_x = min(block_x + DCT_BLOCK_SIZE, width)
            
            block_region = luminance_channel[block_y:block_end_y, block_x:block_end_x]
            
            padded_block = extend_block_to_8x8(block_region)
            
            centered_block = padded_block - 128.0
            dct = dct_forward(centered_block)
            quantized_coefficients = np.rint(dct / JPEG_QUANTIZATION_LUMINANCE).astype(np.int32)
            
            extracted_bits.append(str(extract_lsb_coefficient(quantized_coefficients[u_coord, v_coord])))
    
    return "".join(extracted_bits)


def encrypt_message(input_path, message_text, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Файл {input_path} не найден")
    
    original_image = Image.open(input_path).convert("RGB")
    
    binary_representation = text_to_bitstream(message_text)
    height, width = original_image.size[1], original_image.size[0]
    total_blocks = ((height + DCT_BLOCK_SIZE - 1) // DCT_BLOCK_SIZE) * ((width + DCT_BLOCK_SIZE - 1) // DCT_BLOCK_SIZE)
    
    if len(binary_representation) > total_blocks:
        raise ValueError(
            f"Сообщение слишком длинное для этого изображения.\n"
            f"Требуется блоков: {len(binary_representation)}, доступно: {total_blocks}\n"
            f"Максимальная длина сообщения: {total_blocks // 8} символов"
        )
    
    stego_image = hide_data_in_image(original_image, binary_representation)
    write_jpeg_with_custom_qtable(stego_image, output_path)


def decrypt_message(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл {path} не найден")
    
    try:
        stego_image = Image.open(path).convert("RGB")
        
        length_bits = read_bits_from_image(stego_image, 32)
        
        if len(length_bits) < 32:
            return "[Сообщение не найдено]"
        
        message_length = int(length_bits, 2)
        
        if message_length < 0:
            return "[Некорректная длина сообщения]"
        
        total_bits_needed = 32 + message_length * 8
        
        complete_bit_sequence = read_bits_from_image(stego_image, total_bits_needed)
        
        if len(complete_bit_sequence) < total_bits_needed:
            return "[Не удалось извлечь полное сообщение]"
        
        result = bitstream_to_text(complete_bit_sequence)
        
        if result == "[Ошибка декодирования]":
            return "[В изображении нет корректного скрытого сообщения]"
        
        return result   
        
    except Exception as e:
        return f"[Ошибка: {str(e)}]"
