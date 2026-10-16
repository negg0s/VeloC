#ifndef VELOC_NET_H
#define VELOC_NET_H

#include <veloc.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <unordered_map>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#endif

namespace veloc {
namespace net {

    // ========================================================================
    // 1. Socket Lifecycle & Initialization (RAII)
    // ========================================================================
    class NetInit {
    public:
        NetInit() {
#ifdef _WIN32
            WSADATA wsa;
            WSAStartup(MAKEWORD(2, 2), &wsa);
#endif
        }
        ~NetInit() {
#ifdef _WIN32
            WSACleanup();
#endif
        }
    };

    // ========================================================================
    // 2. High-Performance HTTP/1.1 Request & Response Parser
    // ========================================================================
    struct HttpRequest {
        std::string method;
        std::string path;
        std::string body;
        std::unordered_map<std::string, std::string> headers;

        static bool parse(const char* raw, HttpRequest& req) {
            if (!raw) return false;
            const char* line_end = strstr(raw, "\r\n");
            if (!line_end) return false;

            // Method
            const char* p1 = strchr(raw, ' ');
            if (!p1 || p1 > line_end) return false;
            req.method.assign(raw, p1 - raw);

            // Path
            const char* p2 = strchr(p1 + 1, ' ');
            if (!p2 || p2 > line_end) return false;
            req.path.assign(p1 + 1, p2 - (p1 + 1));

            // Body
            const char* body_start = strstr(raw, "\r\n\r\n");
            if (body_start) {
                req.body = std::string(body_start + 4);
            }
            return true;
        }
    };

    struct HttpResponse {
        int status_code;
        std::string content_type;
        std::string body;

        HttpResponse(int code = 200, const std::string& type = "text/plain", const std::string& b = "")
            : status_code(code), content_type(type), body(b) {}

        std::string serialize() const {
            std::string res;
            res = "HTTP/1.1 " + std::to_string(status_code) + " OK\r\n";
            res += "Content-Type: " + content_type + "\r\n";
            res += "Content-Length: " + std::to_string(body.size()) + "\r\n";
            res += "Connection: close\r\n";
            res += "\r\n";
            res += body;
            return res;
        }
    };

    // ========================================================================
    // 3. Game State Synchronization & Rollback Netcode Engine
    // ========================================================================
    template <typename State, usize HistoryLen = 128>
    class RollbackEngine {
    private:
        State history[HistoryLen];
        u32 confirmed_frame;
        u32 current_frame;

    public:
        RollbackEngine() : confirmed_frame(0), current_frame(0) {}

        void save_frame(u32 frame, const State& state) {
            history[frame % HistoryLen] = state;
            if (frame > current_frame) current_frame = frame;
        }

        const State* get_frame(u32 frame) const {
            if (current_frame - frame >= HistoryLen) return nullptr; // Out of buffer
            return &history[frame % HistoryLen];
        }

        void rollback_to(u32 target_frame) {
            if (target_frame <= current_frame && (current_frame - target_frame) < HistoryLen) {
                current_frame = target_frame;
            }
        }

        u32 get_current_frame() const { return current_frame; }
    };

} // namespace net
} // namespace veloc

#endif // VELOC_NET_H
