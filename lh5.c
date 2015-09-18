/*

Copyright (c) 2011, 2012, Simon Howard

Permission to use, copy, modify, and/or distribute this software
for any purpose with or without fee is hereby granted, provided
that the above copyright notice and this permission notice appear
in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <inttypes.h>

#include <liblhasa-1.0/lha_decoder.h>

typedef struct {
	uint8_t *data;
	size_t data_len;
	unsigned int pos;
} DecompressState;

static void read_file_data(char *filename, uint8_t **data, size_t *len, int start)
{
	FILE *fstream;

	fstream = fopen(filename, "rb");
	assert(fstream != NULL);

	// Read file size:

	if (*len == 0)
	{
		fseek(fstream, 0, SEEK_END);
		*len = (size_t) ftell(fstream) - start;
	}
	fseek(fstream, start, SEEK_SET);

	// Allocate buffer and read data:

	*data = malloc(*len);
	assert(*data != NULL);

	assert(fread(*data, 1, *len, fstream) == *len);

	fclose(fstream);
}

// Callback function used by decoder to read compressed data.

static size_t read_compressed_data(void *buf, size_t buf_len, void *user)
{
	DecompressState *state = user;
	size_t result;

	// Copy as many bytes of data as possible:

	result = state->data_len - state->pos;

	if (buf_len < result) {
		result = buf_len;
	}

	memcpy(buf, state->data + state->pos, result);

	// Update stream position.

	state->pos += result;

	return result;
}

// Create an in-memory decoder, reading from the specified buffer.

static LHADecoder *create_decoder(DecompressState *state,
                                  uint8_t *data, size_t data_len,
                                  char *algorithm, size_t uncompressed_len)
{
	LHADecoderType *dtype;
	LHADecoder *decoder;

	// Data structure for reading compressed data from buffer.

	state->data = data;
	state->data_len = data_len;
	state->pos = 0;

	// Create decoder.

	dtype = lha_decoder_for_name(algorithm);
	assert(dtype != NULL);

	decoder = lha_decoder_new(dtype, read_compressed_data, state,
	                          uncompressed_len);
	assert(decoder != NULL);

	return decoder;
}

int main(int argc, char *argv[])
{
	uint8_t *data;
	unsigned int i;
	LHADecoder *decoder;
	DecompressState state;
	uint8_t buf[256 * 256];
	size_t len;
	size_t data_len = 0;
	int uncompressed_len = 0;
	int start = 0;

	assert(argc >= 3 && argc <= 5);
	
	sscanf(argv[2], "%d", &uncompressed_len);
	assert(uncompressed_len > 0);
	
	if (argc > 3)
	{
		start = -1;
		sscanf(argv[3], "%d", &start);
		assert(start >= 0);
	}

	if (argc > 4)
	{
		int tmp = -1;
		sscanf(argv[4], "%d", &tmp);
		assert(tmp >= 0);
		data_len = tmp;
	}

        read_file_data(argv[1], &data, &data_len, start);

	// Create decoder and decompress:

	decoder = create_decoder(&state, data, data_len, "-lh5-", uncompressed_len);

	while ( (len = lha_decoder_read(decoder, buf, sizeof(buf))) != 0)
		fwrite(buf, len, 1, stdout);

	lha_decoder_free(decoder);

	free(data);
	return 0;
}

