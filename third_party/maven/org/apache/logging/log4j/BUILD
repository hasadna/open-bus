java_library(
    name = "log4j_api",
    exports = [
        "//external:jar/org/apache/logging/log4j/log4j_api"
    ],
    licenses = [
        "permissive"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "log4j_to_slf4j",
    exports = [
        "//external:jar/org/apache/logging/log4j/log4j_to_slf4j"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        ":log4j_api"
    ],
    visibility = [
        "//visibility:public"
    ]
)


