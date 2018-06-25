java_library(
    name = "spring_aop",
    exports = [
        "//external:jar/org/springframework/spring_aop"
    ],
    licenses = [
        "permissive"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_beans",
    exports = [
        "//external:jar/org/springframework/spring_beans"
    ],
    licenses = [
        "permissive"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_context",
    exports = [
        "//external:jar/org/springframework/spring_context"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        ":spring_aop",
        ":spring_beans",
        ":spring_expression"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_core",
    exports = [
        "//external:jar/org/springframework/spring_core"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        ":spring_jcl"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_expression",
    exports = [
        "//external:jar/org/springframework/spring_expression"
    ],
    licenses = [
        "permissive"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_jcl",
    exports = [
        "//external:jar/org/springframework/spring_jcl"
    ],
    licenses = [
        "permissive"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_web",
    exports = [
        "//external:jar/org/springframework/spring_web"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        ":spring_beans"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_webmvc",
    exports = [
        "//external:jar/org/springframework/spring_webmvc"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        ":spring_aop",
        ":spring_context",
        ":spring_expression"
    ],
    visibility = [
        "//visibility:public"
    ]
)


