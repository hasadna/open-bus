#load("//common/spring:spring.bzl", "boot_jar")

java_binary(
    name = "siri1_java_binary",
    srcs = glob(["**/*.java"]),
    main_class = "org.hasadna.bus.BusApplication",
    visibility = ["//visibility:public"],
    deps = [
        "//third_party/maven/ch/qos/logback:logback_core",
        "//third_party/maven/org/slf4j:slf4j_api",
        "//third_party/maven/org/springframework:spring_beans",
        "//third_party/maven/org/springframework:spring_context",
        "//third_party/maven/org/springframework:spring_core",
        "//third_party/maven/org/springframework:spring_web",
        "//third_party/maven/org/springframework:spring_webmvc",
        "//third_party/maven/org/springframework/boot:spring_boot",
        "//third_party/maven/org/springframework/boot:spring_boot_autoconfigure",
        "//third_party/maven/org/springframework/boot:spring_boot_starter_web",
        "//third_party/maven/org/springframework/boot:spring_boot_loader_tools",
    ],
)

#boot_jar(
#    name = "siri1",
#    #srcs = glob(["**/*.java"]),
#    #main_class = "org.hasadna.bus.BusApplication",
#    #visibility = ["//visibility:public"],
#    target = "//common/siri1:siri1_java_binary",
#)
