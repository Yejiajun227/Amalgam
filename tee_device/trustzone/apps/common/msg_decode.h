#include <msgpack.h>
// #include "crypto.h"
#include "tz_data.h"

// msgpack_sbuffer encode_string_list(char **in, int count);


int decode_string_list(const char *bytes, int bytes_size, char **out);


int decode_smatrix(char *bytes, int byte_size, SMatrix *out_m);
