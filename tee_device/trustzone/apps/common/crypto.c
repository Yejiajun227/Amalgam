#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/rand.h>
#include <openssl/rsa.h>
#include <openssl/sha.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "crypto.h"
// #include "array_msg.h"


#define AES_KEY_LEN 32
#define AES_KEY_IV 16

char *data_source_pk_path;

unsigned char aes_key[AES_KEY_LEN] = {0};
unsigned char aes_iv[AES_KEY_IV] = {1};


char* rsa_pem_encrypt(unsigned char *str, char *pk_path)
{
	char *p_en = NULL;
	RSA *p_rsa = NULL;
    // BIO是openssl定义的结构体  https://ayanami-daisuki.github.io/2022/06/22/OpenSSL/#pem-5
	BIO *file = NULL;
    unsigned char *new_str = NULL;

	if((file = BIO_new_file(pk_path, "rb")) == NULL)
	{
        perror("BIO open file error");
		goto End;
	}
	//2.从公钥中获取 加密的秘钥
    // PEM_read_bio_RSAPublicKey()
    // PEM_read_RSAPublicKey
	if((p_rsa = PEM_read_bio_RSA_PUBKEY(file, NULL, NULL, NULL)) == NULL)
	{
        perror("PEM_read_bio_RSA_PUBKEY error");
		goto End;
	}

	int length = sizeof(str) -1;    // 待加密字符串长度
	p_en = (char *)malloc(256);
	if(!p_en)
	{
		perror("malloc error");
		goto End;
	}
	memset(p_en, 0, 256);
	//5.对内容进行加密
    // OAEP 默认采用sha1,这里需要使用sha-256 因此需要手动在外部padding
    // https://developer.aliyun.com/article/693527
    // int RSA_padding_add_PKCS1_OAEP_mgf1(unsigned char *to, int tlen,
    //                                 const unsigned char *from, int flen,
    //                                 const unsigned char *param, int plen,
    //                                 const EVP_MD *md, const EVP_MD *mgf1md);
    // 指定sha256 
    const EVP_MD *md = EVP_sha256();
    new_str = (unsigned char*) malloc(256);

    if(RSA_padding_add_PKCS1_OAEP_mgf1(new_str, 256, (const unsigned char*)str, length, NULL, 0, md, md) < 0)
    {
        perror("RSA_padding_add_PKCS1_OAEP_mgf1() error");
        goto End;
    }

	if(RSA_public_encrypt(256, (unsigned char*)new_str, (unsigned char*)p_en, p_rsa, RSA_NO_PADDING) < 0)
	{
		perror("RSA_public_encrypt() error");
		goto End;
	}
End:
	if(p_rsa) RSA_free(p_rsa);
    BIO_free(file);
    if (new_str)free(new_str);
	return p_en;
}


void Init_aes_key()
{
    RAND_bytes(aes_key, AES_KEY_LEN);
}


void Generate_Enc_Key(char *data_source_pk_path, int data_source_pk_pathlen, char *out_key)
{
    // enc key
    // char *path = "/root/projects/trustzone-code/operator/python/config/public_key.pem";
    char *res = rsa_pem_encrypt(aes_key, data_source_pk_path);
    // return 
    memcpy(out_key, res, 256);
    // return res;
}


int aes_ecb_encrypt(unsigned char* inStr, unsigned char* outStr)
{
    //加密
    int encLen = 0;
    int outlen = 0;

    EVP_CIPHER_CTX *ctx;
    ctx = EVP_CIPHER_CTX_new();
    
    EVP_CipherInit_ex(ctx, EVP_aes_256_ecb(), NULL, aes_key, aes_iv, 1);
    // set padding
    // EVP_PADDING_PKCS7       1
    // EVP_PADDING_ISO7816_4   2
    // EVP_PADDING_ANSI923     3
    // EVP_PADDING_ISO10126    4
    // EVP_PADDING_ZERO        5
    EVP_CIPHER_CTX_set_padding(ctx, 1);

    EVP_CipherUpdate(ctx, outStr, &outlen, inStr, sizeof(inStr) -1);
    encLen = outlen;
    EVP_CipherFinal(ctx, outStr+outlen, &outlen);
    encLen += outlen;
    EVP_CIPHER_CTX_free(ctx);

    // printf("in func enclen is%d\n",encLen);

    return encLen;
}


void aes_ecb_decrypt(const unsigned char* inStr, int inStr_len, unsigned char* outStr)
{
    //
    int decLen = 0;
    int outlen = 0;

    EVP_CIPHER_CTX *ctx;
    ctx = EVP_CIPHER_CTX_new();
    EVP_CipherInit_ex(ctx, EVP_aes_256_ecb(), NULL, aes_key, aes_iv, 0);
    EVP_CIPHER_CTX_set_padding(ctx, 1);

    EVP_CipherUpdate(ctx, outStr, &outlen, inStr, inStr_len);
    decLen = outlen;
    EVP_CipherFinal(ctx, outStr+outlen, &outlen);
    decLen += outlen;
    EVP_CIPHER_CTX_free(ctx);
    
    outStr[decLen] = '\0';
}


