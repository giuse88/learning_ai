#include <iostream>
#include <cstdlib>

#include <httplib.h>
#include <nlohmann/json.hpp>

using namespace std;
using json = nlohmann::json;

const char * KEY = "ANTHROPIC_API_KEY";
const char * MODEL = "claude-sonnet-5";
const char * SYSTEM = "You are a concise assistant.";
const char * HOST = "https://api.anthropic.com";

json format_message(const json& messages) {
    json body;
    body["model"] = MODEL;
    body["max_tokens"] = 4096;
    body["system"] = SYSTEM;
    body["messages"] = messages;
    return body;
}

json send_message(const json& body, const char * api_key) {
    httplib::Client client(HOST);       // scheme + host only; the path goes in Post()
    client.set_connection_timeout(10);  // seconds
    client.set_read_timeout(120);       // Claude can take a while to write a long answer

    httplib::Headers headers = {
        {"x-api-key", api_key},
       {"anthropic-version", "2023-06-01"}
    };
    auto res = client.Post("/v1/messages", headers, body.dump(), "application/json");

    if (!res) {
        throw runtime_error("request failed: " + httplib::to_string(res.error()));
    }
    // got a response, but the API rejected the request; the body explains why
    if (res->status != 200) {
        throw runtime_error("HTTP " + to_string(res->status) + ": " + res->body);
    }
    return json::parse(res->body);
}

const char * load_antropic_key() {

    const char* env_p = std::getenv(KEY);

    if (env_p == nullptr) {
        std::cerr << "Variable " << KEY << " not set" << std::endl;
        exit(-1);
    }

    return env_p;
}


int main() {
    std::cout << "Simple Harness" << std::endl;
    auto key = load_antropic_key();

    json messages = json::array();

    try {

        while (true) {
        char * input = nullptr;
        cout << "USER >";
        cin << input; 
        messages.push_back({{"role", "user"}, {"content", user_input}});

        json reply = send_message(format_message(messages), key);
        if (reply["stop_reason"] == "refusal") {
            std::cerr << "Claude declined to answer" << std::endl;
            return 1;
        }

        for (const auto& block : reply["content"]) {
            if (block["type"] == "text") {
                std::cout << "AGENT >" << block["text"].get<string>() << std::endl;
            }
        }
    } catch (const exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
    }

    return 0;
}
