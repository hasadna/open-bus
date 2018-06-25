java_library(
    name = "spring_boot",
    exports = [
        "//external:jar/org/springframework/boot/spring_boot"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        "//third_party/maven/org/springframework:spring_context"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_boot_autoconfigure",
    exports = [
        "//external:jar/org/springframework/boot/spring_boot_autoconfigure"
    ],
    licenses = [
        "permissive"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_boot_loader",
    exports = [
        "//external:jar/org/springframework/boot/spring_boot_loader"
    ],
    licenses = [
        "permissive"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_boot_loader_tools",
    exports = [
        "//external:jar/org/springframework/boot/spring_boot_loader_tools"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        "//third_party/maven/org/apache/commons:commons_compress",
        "//third_party/maven/org/springframework:spring_core"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_boot_starter",
    exports = [
        "//external:jar/org/springframework/boot/spring_boot_starter"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        "//third_party/maven/javax/annotation:javax_annotation_api",
        "//third_party/maven/org/springframework:spring_core",
        "//third_party/maven/org/yaml:snakeyaml",
        ":spring_boot",
        ":spring_boot_autoconfigure",
        ":spring_boot_starter_logging"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_boot_starter_json",
    exports = [
        "//external:jar/org/springframework/boot/spring_boot_starter_json"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        "//third_party/maven/com/fasterxml/jackson/core:jackson_databind",
        "//third_party/maven/com/fasterxml/jackson/datatype:jackson_datatype_jdk8",
        "//third_party/maven/com/fasterxml/jackson/datatype:jackson_datatype_jsr310",
        "//third_party/maven/com/fasterxml/jackson/module:jackson_module_parameter_names"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_boot_starter_logging",
    exports = [
        "//external:jar/org/springframework/boot/spring_boot_starter_logging"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        "//third_party/maven/ch/qos/logback:logback_classic",
        "//third_party/maven/org/apache/logging/log4j:log4j_to_slf4j",
        "//third_party/maven/org/slf4j:jul_to_slf4j"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_boot_starter_tomcat",
    exports = [
        "//external:jar/org/springframework/boot/spring_boot_starter_tomcat"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        "//third_party/maven/org/apache/tomcat/embed:tomcat_embed_core",
        "//third_party/maven/org/apache/tomcat/embed:tomcat_embed_el",
        "//third_party/maven/org/apache/tomcat/embed:tomcat_embed_websocket"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "spring_boot_starter_web",
    exports = [
        "//external:jar/org/springframework/boot/spring_boot_starter_web"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        "//third_party/maven/org/hibernate/validator:hibernate_validator",
        "//third_party/maven/org/springframework:spring_web",
        "//third_party/maven/org/springframework:spring_webmvc",
        ":spring_boot_starter",
        ":spring_boot_starter_json",
        ":spring_boot_starter_tomcat"
    ],
    visibility = [
        "//visibility:public"
    ]
)


