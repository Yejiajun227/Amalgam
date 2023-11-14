

char* rsa_pem_encrypt(unsigned char *str, char *pk_path);

void Init_aes_key();

void Generate_Enc_Key(char *data_source_pk_path, int data_source_pk_pathlen, char *out_key);

int aes_ecb_encrypt(unsigned char* inStr, unsigned char* outStr);

void aes_ecb_decrypt(const unsigned char* inStr, int inStr_len, unsigned char* outStr);