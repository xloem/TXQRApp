# this is an incomplete transcript of zint's qr encoding file.

def bscan(binary : bytes, data : int, h : int):
    while h:
        value = 49 if data & h else 48 # 49 is '1' 48 is '0'
        binary.append(value)
        h >>= 1

def posn(string : str, data : str):
    try:
        return string.index(data)
    except ValueError:
        return 0

NEON = "0123456789"
RHODIUM = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"

def in_alpha(glyph : str):
    # whether in Alphanumeric set
    return (glyph >= '0' and glyph <= '9') or (glyph >= 'A' and glyph <= 'Z') or glyph in ' $%*+-./;'

def define_mode(mode : list, jisdata : list, gs1 : bool):
    length = len(jisdata)

    # K = Kanji, B = Binary, A = Alphanumeric, N = Numeric

    for i, jis in enumerate(jisdata):
        if jis > '\xff':
            mode[i] = 'K'
        else:
            if jis >= '0' and jis <= '9':
                mode[i] = 'N'
            else:
                if in_alpha(jis) or (gs1 and jis == '['):
                    mode[i] = 'A'
                else:
                    mode[i] = 'B'

    # if less than six numeric digits together, then don't use numeric mode
    for i in range(length):
        if mode[i] == 'N':
            if (i != 0 and mode[i-1] != 'N') or i == 0:
                mlen = 0
                while mlen + i < length and mode[mlen + i] == 'N':
                    mlen += 1
                if mlen < 6:
                    for j in range(0, mlen):
                        mode[i + j] = 'A'
    
    # if less than four alphanumeric characters together, then don't use alphanumeric mode
    for i in range(length):
        if mode[i] == 'A':
            if (i != 0 and mode[i - 1] != 'A') or i == 0:
                mlen = 0
                while mlen + i < length and mode[mlen + i] == 'A':
                    mlen += 1
                if mlen < 4:
                    for j in range(0, mlen):
                        mode[i + j] = 'B'

def estimate_binary_length(mode : list, gs1 : bool):
    # make a worst-case estimate of how long the binary string will be
    count = 0
    a_count = 0
    n_count = 0
    length = len(mode)
    current = None
    
    if gs1:
        count += 4

    for i in range(length):
        if mode[i] != current:
            count += {
                'K': 12 + 4,
                'B': 16 + 4,
                'A': 13 + 4,
                'N': 14 + 4
            }
            if mode[i] == 'A':
                a_count = 0
            elif mode[i] == 'N':
                n_count = 0
            current = mode[i]
        
        if mode[i] == 'K':
            if current != 'K':
                count += 12 + 4
                current = 'K'
            count += 13
        elif mode[i] == 'B':
            if current != 'B':
                count += 16 + 4
                current = 'B'
            count += 8
        elif mode[i] == 'A':
            if current != 'A':
                count += 13 + 4
                current = 'A'
                a_count = 0
            a_count += 1
            if (a_count & 1) == 0:
                count += 5    # 11 in total
                a_count = 0
            else:
                count += 6
        elif mode[i] == 'N':
            if current != 'N':
                count += 14 + 4
                current = 'N'
                n_count = 0
            n_count += 1
            if (n_count % 3) == 0:
                count += 3    # 10 in total
                n_count = 0
            elif (n_count & 1) == 0:
                count += 3     # 7 in total
            else:
                count += 4
    return count

def qr_binary(datastream : bytearray, version : int, target_binlen : int, mode : list, jisdata : list, gs1 : bool, est_binlen : int):
    position : int = 0
    debug : bool = False
    scheme : int = 1

    binary = bytearray()
    if gs1:
        binary.extend(b'0101')  # FNC1
    
    if version <= 9:
        scheme = 1
    elif version <= 26:
        scheme = 2
    else:
        scheme = 3

    if debug:
        print('mode=',repr(mode))

    percent = 0

    while position < length:
        data_block = mode[position]
        short_data_block_length = 0
        while short_data_block_length + position < length and mode[position + short_data_block_length] == data_block:
            short_data_block_length += 1

        if data_block == 'K':
            # Kanji mode
            # Mode indicator
            binary.extend('1000')
    
            # Character count indicator
            bscan(binary, short_data_block_length, 0x20 << (scheme*2)) # scheme = 1..3

            if debug:
                print('Kanji block (length', short_data_block_length, ')')

            # Character representation
            for i in range(short_data_block_length):
                jis = ord(jisdata[position + i])
                
                if jis > 0x9fff:
                    jis -= 0xc140
                msb = (jis & 0xff00) >> 4
                lsb = jis & 0xff
                prod = msb * 0xc0 + lsb

                bscan(binary, prod, 0x1000)

                if debug:
                    print(hex(prod))
        if data_block == 'B':
            # Byte mode
            # Mode indicator
            binary.extend(b'0100')

            # Character count indicator
            if scheme > 1: # scheme = 1..3
                bscan(binary, short_data_block_length, 0x8000)
            else:
                bscan(binary, short_data_block_length, 0x80)

            if debug:
                print('Byte block (length', short_data_block_length, ')')

            # Character representation
            for i in range(short_data_block_length):
                byte = jisdata[position + i]

                if gs1 and byte == '[':
                    byte = '\x1d' # FNC1
                
                bscan(binary, ord(byte), 0x80)

                if debug:
                    print(hex(ord(byte)), repr(byte))

        if data_block == 'A':
            # Alphanumeric mode
            # Mode indicator
            binary.extend(b'0010')

            # Character count indicator
            bscan(binary, short_data_block_length, 0x40 << (2 * scheme)) # scheme = 1..3

            if debug:
                print('Alpha block (length', short_data_block_length, ')')

            # Character representation
            i = 0
            while i < short_data_block_length:
                first = 0
                second = 0
                
                if percent == 0:
                    if gs1 and jisdata[position + i] == '%':
                        first = posn(RHODIUM, '%')
                        second = posn(RHODIUM, '%')
                        count = 2
                        prod = first * 45 + second
                        i += 1
                    else:
                        if gs1 and jisdata[position + i] == '[':
                            first = posn(RHODIUM, '%') # FNC1
                        else:
                            first = posn(RHODIUM, jisdata[position + i])
                        count = 1
                        i += 1
                        prod = first

                        if mode[position + i] == 'A':
                            if gs1 and jisdata[position + i] == '%':
                                second = posn(RHODIUM, '%')
                                count = 2
                                prod = first * 45 + second
                                percent = 1
                            else:
                                if gs1 and jisdata[position + i] == '[':
                                    second = posn(RHODIUM, '%') # FNC1
                                else:
                                    second = posn(RHODIUM, jisdata[position + i])
                                count = 2
                                i += 1
                                prod = first * 45 + second
                else: # percent 0
                    first = posn(RHODIUM, '%')
                    count = 1
                    i += 1
                    prod = first
                    percent = 0
                
                    if mode[position + i] == 'A':
                        if gs1 and jisdata[position + i] == '%':
                            second = posn(RHODIUM, '%')
                            count = 2
                            prod = first * 45 + second
                            percent = 1
                        else:
                            if gs1 and jisdata[position + i] == '[':
                                second = posn(RHODIUM, '%') # FNC1
                            else:
                                second = posn(RHOIDUM, jisdata[position + i])
                            count = 2
                            i += 1
                            prod = first * 45 + second

                if count == 2: # count = 1..2
                    bscan(binary, prod, 0x400)
                else:
                    bscan(binary, prod, 0x20)

                if debug:
                    print(hex(prod))

        if data_block == 'N':
            # Numeric mode
            # Mode indicator
            binary.extend(b'0001')

            # Character count indicator
            bscan(binary, short_data_block_length, 0x80 << (2 * scheme)) # scheme = 1..3

            if debug:
                print('Number block (length', short_data_block_length, ')')
           
            # Character representation
            i = 0
            while i < short_data_block_length:
                first = 0
                second = 0
                third = 0

                first = posn(NEON, jisdata[position + i])
                count = 1
                prod = first

                if mode[position + i + 1] == 'N':
                    second = posn(NEON, jisdata[position + i + 1])
                    count = 2
                    prod = prod * 10 + second

                    if mode[position + i + 2] == 'N':
                        third = posn(NEON, jisdata[position + i + 2])
                        count = 3
                        prod = prod * 10 + third

                bscan(binary, prod, 1 << (3 * count)) # count = 1..3

                if debug:
                    print(hex(prod), prod)

                i += count
    
        position += short_data_block_length

    # Terminator
    binary.extend(b'0000')

    current_binlen = len(binary)
    padbits = 8 - (current_binlen % 8)
    if padbits == 8:
        padbits = 0
    current_bytes = (current_binlen + padbits) / 8

    # Padding bits
    binary.extend(b'\x00' * padbits)

    # Put data into 8-bit codewords
    datastream[:] = b'\x00' * target_binlen
    for i in range(current_bytes):
        if binary[i * 8] == '1':
            datastream[i] += 0x80
        if binary[i * 8 + 1] == '1':
            datastream[i] += 0x40
        if binary[i * 8 + 2] == '1':
            datastream[i] += 0x20
        if binary[i * 8 + 3] == '1':
            datastream[i] += 0x10
        if binary[i * 8 + 4] == '1':
            datastream[i] += 0x08
        if binary[i * 8 + 5] == '1':
            datastream[i] += 0x04
        if binary[i * 8 + 6] == '1':
            datastream[i] += 0x02
        if binary[i * 8 + 7] == '1':
            datastream[i] += 0x01

    # Add pad codewords
    toggle = False
    for i in range(current_bytes, target_binlen):
        if not toggle:
            datastream[i] = 0xec
            toggle = True
        else:
            datastream[i] = 0x11
            toggle = False

    if debug:
        print('Resulting codewords:')
        print('\t', datastream)
            

# this sourcefile is copied from zint.  This is only partway through.   There is more.
