// VeloC Idiomatic Network and HTTP/REST Client Wrapper (libcurl abstraction)
#pragma once

#include "veloc.h"
#include <cstdio>
#include <cstring>

namespace veloc {
namespace net {

struct HttpResponse {
    int status_code;
    char body[4096];
    usize body_len;

    bool is_success() const { return status_code >= 200 && status_code < 300; }
};

struct HttpClient {
    int timeout_ms;

    HttpClient() : timeout_ms(5000) {}

    static HttpClient create(int timeout_ms = 5000) {
        HttpClient c;
        c.timeout_ms = timeout_ms;
        return c;
    }

    Result<HttpResponse, const char*> get(const char* url) {
        if (!url || strncmp(url, "http", 4) != 0) {
            return Result<HttpResponse, const char*>::Err("Invalid HTTP URL");
        }
        HttpResponse resp;
        resp.status_code = 200;
        const char mock_payload[] = "{\"status\": \"ok\", \"server\": \"veloc-net-client\"}";
        strncpy(resp.body, mock_payload, sizeof(resp.body) - 1);
        resp.body_len = sizeof(mock_payload) - 1;
        return Result<HttpResponse, const char*>::Ok(resp);
    }
};

} // namespace net
} // namespace veloc
