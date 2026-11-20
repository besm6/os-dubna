// ovl2bin - expand an overlay of the overlay catalog (its RLE stream, as
// stored on a system volume) into the image of words: ovl2bin < ovl > bin
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define WORD_BYTES 6

// Read a 48-bit word (6 bytes) into a uint64_t in big-endian order
int read_word(uint8_t *buffer, uint64_t *word) {
    if (fread(buffer, 1, WORD_BYTES, stdin) != WORD_BYTES) {
        return 0; // EOF or error
    }
    *word = ((uint64_t)buffer[0] << 40) |
            ((uint64_t)buffer[1] << 32) |
            ((uint64_t)buffer[2] << 24) |
            ((uint64_t)buffer[3] << 16) |
            ((uint64_t)buffer[4] << 8)  |
            (uint64_t)buffer[5];
    return 1;
}

// Write a 48-bit word (6 bytes) from a uint64_t in big-endian order
int write_word(uint64_t word) {
    uint8_t buffer[WORD_BYTES];
    buffer[0] = (word >> 40) & 0xFF;
    buffer[1] = (word >> 32) & 0xFF;
    buffer[2] = (word >> 24) & 0xFF;
    buffer[3] = (word >> 16) & 0xFF;
    buffer[4] = (word >> 8)  & 0xFF;
    buffer[5] = word & 0xFF;
    if (fwrite(buffer, 1, WORD_BYTES, stdout) != WORD_BYTES) {
        return 0;
    }
    return 1;
}

int main() {
    uint8_t buffer[WORD_BYTES];
    uint64_t header, to_be_repeated;
    uint64_t flag, repeat_count, data_count;
    uint64_t word;
    size_t i;

    while (1) {
        // Read header (6 bytes)
        if (!read_word(buffer, &header)) {
            fprintf(stderr, "Error: Unexpected end of input while reading header\n");
            return 1;
        }

        // Extract fields (big-endian)
        flag = (header >> 47) & 1;
        repeat_count = (header >> 15) & 0x7FFF; // Bits 29-15
        data_count = header & 0x7FFF;          // Bits 14-0

        // Termination condition: both counts are zero
        if (repeat_count == 0 && data_count == 0) {
            break;
        }

        // If flag is set and repeat_count is non-zero, read to_be_repeated
        if (flag && repeat_count > 0) {
            if (!read_word(buffer, &to_be_repeated)) {
                fprintf(stderr, "Error: Unexpected end of input while reading to_be_repeated\n");
                return 1;
            }
        }

        // Copy data_count words from stdin to stdout
        for (i = 0; i < data_count; i++) {
            if (!read_word(buffer, &word)) {
                fprintf(stderr, "Error: Unexpected end of input while reading data word\n");
                return 1;
            }
            if (!write_word(word)) {
                fprintf(stderr, "Error: Failed to write data word to stdout\n");
                return 1;
            }
        }

        // Output repeat_count words: to_be_repeated if flag is set, else zero
        word = flag ? to_be_repeated : 0;
        for (i = 0; i < repeat_count; i++) {
            if (!write_word(word)) {
                fprintf(stderr, "Error: Failed to write repeated word to stdout\n");
                return 1;
            }
        }
    }

    return 0;
}
