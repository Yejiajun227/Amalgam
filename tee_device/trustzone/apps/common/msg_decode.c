// #include <openssl/bio.h>
// #include <openssl/err.h>
// #include <openssl/evp.h>
// #include <openssl/pem.h>
// #include <openssl/rand.h>
// #include <openssl/rsa.h>
// #include <openssl/sha.h>
#include <stdio.h>
#include <string.h>
#include "msg_decode.h"
#include "crypto.h"
#include "tz_data.h"


int decode_string_list(const char *bytes, int bytes_size, char **out) {
    msgpack_sbuffer sbuf;
    msgpack_sbuffer_init(&sbuf);
    sbuf.data = (char *)bytes;
    sbuf.size = bytes_size;

    msgpack_zone mempool;
    msgpack_zone_init(&mempool, 2048);

    msgpack_object deserialized;
    msgpack_unpack(sbuf.data, sbuf.size, NULL, &mempool, &deserialized);

    assert(deserialized.type == MSGPACK_OBJECT_ARRAY);

    assert((deserialized.via.array.ptr + 0)->type == MSGPACK_OBJECT_POSITIVE_INTEGER);
    int count = (deserialized.via.array.ptr + 0)->via.u64; // count 记录字符串数组中元素个数

    for (int i = 1; i < (int)deserialized.via.array.size; i++) {
        msgpack_object *o = (deserialized.via.array.ptr + i);

        assert(o->type == MSGPACK_OBJECT_BIN);
        int slen = (o->via.str.size + 1);
        char *s = (char *)malloc(slen * sizeof(char));
        memcpy(s, o->via.str.ptr, slen - 1);
        s[slen - 1] = '\0';
        // 外部需要free
        out[i - 1] = s;
        // tlogd("cur str %s %d", s, slen);
        // tlogd("cur str %s %d", (char*) , slen);
    }
    return count;
}


int decode_smatrix(char *bytes, int byte_size, SMatrix *out_m)
{
    // decrypt 
    // void aes_ecb_decrypt(char* inStr, int inStr_len, char* outStr);
    char *outstr = (char *)malloc(sizeof(char)*byte_size);
    aes_ecb_decrypt((unsigned char *)bytes, byte_size, (unsigned char *)outstr);

    msgpack_unpacked msg;
    msgpack_unpacked_init(&msg);
    // 测试这里的sizeof 和 strlen
    msgpack_unpack_return ret = msgpack_unpack_next(&msg, outstr, byte_size, NULL);
    int row = 0;
    int col = 0;

    if (ret == MSGPACK_UNPACK_SUCCESS) {
        // 解析成功，获取反序列化后的数据
        msgpack_object obj = msg.data;

        matrix_initialize(out_m, obj.via.array.size - 1, obj.via.array.ptr[0].via.array.size);

        if (obj.type == MSGPACK_OBJECT_ARRAY) {
            row = obj.via.array.size;
            col = obj.via.array.ptr[0].via.array.size;

            // printf("Row: %d, Column: %d\n", row, col);

            for (int i=0; i<col; i++)
            {
                int slen = (obj.via.array.ptr[0].via.array.ptr[i].via.str.size + 1);
                char *s = (char *)malloc(slen * sizeof(char));
                memcpy(s, obj.via.array.ptr[0].via.array.ptr[i].via.str.ptr, slen - 1);
                s[slen-1] = '\0';
                out_m->head[i] = s;
                // printf("%s ", out_m->head[i]);
            }
            // printf("\n");

            for (int i = 1; i < row; ++i) {
                for (int j = 0; j < col; ++j) {
                    // char* value = obj.via.array.ptr[i].via.array.ptr[j].via.str;
                    
                    int slen = (obj.via.array.ptr[i].via.array.ptr[j].via.str.size + 1);
                    char *s = (char *)malloc(slen * sizeof(char));
                    memcpy(s, obj.via.array.ptr[i].via.array.ptr[j].via.str.ptr, slen - 1);
                    s[slen-1] = '\0';
                    out_m->data[(i-1)*col+j] = s;
                    // printf("%s ", out_m->data[i*col+j]);
                }
                // printf("%s ", out_m->data[i*col]);
                // if (i%50 ==0)printf("\n");
                // printf("\n");
            }
        }
    }
    msgpack_unpacked_destroy(&msg);
    free(outstr);
    return row - 1;
}
