#include <msgpack.h>
#include "msg_encode.h"


msgpack_sbuffer encode_string_list(char **in, int count) {
    msgpack_sbuffer sbuf;
    msgpack_sbuffer_init(&sbuf);
    msgpack_packer pk;
    msgpack_packer_init(&pk, &sbuf, msgpack_sbuffer_write);
    msgpack_pack_array(&pk, count);
    // msgpack_pack_int(&pk, count);

    for (int i = 0; i < count; i++) {
        // char *row = in[i];
        int str_len = strlen(in[i]);
        msgpack_pack_v4raw(&pk, str_len);
        msgpack_pack_v4raw_body(&pk, in[i], str_len);
        // msgpack_pack_bin_with_body(&pk, row, 32);
    }

    return sbuf;
}
