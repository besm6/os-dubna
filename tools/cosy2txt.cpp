//
// COSY file encoding.
//
// Copyright (c) 2022-2023 Leonid Broukhis, Serge Vakulenko
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//

#include <filesystem>
#include <fstream>
#include <sstream>

// #include "besm6_arch.h"
#include "encoding.h"

//
// Card '*read old' has a special representation.
// Note the space symbol is not packed.
// It is impossible to obtain with a regular encode_cosy() routine.
//
static const std::string COSY_READ_OLD = "*READ OLD\312\n\n";

//
// Card '*end file' has two alternative representations.
//
static const std::string COSY_END_FILE_REGULAR = "*END\201FILE\312\n\n";

//
// Legacy variant produced by *EDIT.
// Note the space symbol is not packed,
// and extra space is appended.
//
static const std::string COSY_END_FILE_LEGACY = "*END FILE \311\n";

//
// Read COSY card from an input stream and place it into a string.
// Return false on EOF or failure.
//
bool get_line_cosy(std::istream &input, std::string &line)
{
    // Read words up to '\n' in lower byte.
    line.clear();
    do {
        if (line.size() >= 14 * 6) {
            // A valid COSY line can have up to 14 words, or 84 bytes.
            return false;
        }

        // Read next word.
        line.push_back(input.get());
        line.push_back(input.get());
        line.push_back(input.get());
        line.push_back(input.get());
        line.push_back(input.get());
        line.push_back(input.get());
        if (!input.good()) {
            // Premature end of file.
            return false;
        }
    } while (line.back() != '\n');
    return true;
}

//
// Recognize card '*read old'.
//
bool is_read_old_cosy(const std::string &line)
{
    return line == COSY_READ_OLD;
}

//
// Recognize card '*end file'.
// It has two alternative representations.
//
bool is_end_file_cosy(const std::string &line)
{
    return (line == COSY_END_FILE_REGULAR) || (line == COSY_END_FILE_LEGACY);
}

//
// Decode string from COSY format.
// Return false on failure.
//
bool decode_cosy(std::string &line)
{
    std::stringstream result;

    for (uint8_t ch : line) {
        if (ch == '\n') {
            // End of line.
            break;
        }
        if (ch >= 0201 && ch <= 0323) {
            // Unpack spaces.
            while (ch-- > 0200) {
                result << ' ';
            }
            continue;
        }
        if (ch < ' ' || ch > 0177) {
            // Bad byte.
            return false;
        }
        utf8_putc(koi7_to_unicode[ch], result);
    }
    line = result.str();

    // Remove trailing spaces.
    line.erase(line.find_last_not_of(" ") + 1);
    return true;
}

//
// Convert file.bin in COSY format to file.txt.
// Return true when succeeded.
//
int main()
{
    // Open binary file.
    auto & input{std::cin};
    if (!input.good()) {
        // No binary file.
        return false;
    }

    // Open text file for write.
    auto & output{std::cout};
    if (!output.good()) {
        // Cannot write.
        return false;
    }

    std::string line;
    for (;;) {
        if (!get_line_cosy(input, line)) {
            // End of file - card '*read old' is missing.
            return false;
        }
        if (is_read_old_cosy(line)) {
            // Valid '*read old' found.
            break;
        }
        if (!decode_cosy(line)) {
            // Bad data.
            return false;
        }
        output << line << '\n';
    }

    // Check next card.
    if (!get_line_cosy(input, line)) {
        // Cannot read '*end file' card.
        return false;
    }
    if (!is_end_file_cosy(line)) {
        // Card '*end file' is missing.
        return false;
    }
    return true;
}

