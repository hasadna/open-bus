package(default_visibility = ["//visibility:public"])

proto_library(
    name = "data_proto",
    srcs = ["data.proto"],
)

java_proto_library(
    name = "data_java_proto",
    deps = [":data_proto"],
)

java_binary(
    name = "data_checker_tool",
    srcs = [
        "DataCheckerTool.java",
    ],
    main_class = "bazel.tools.DataCheckerTool",
    deps = [
        ":data_java_proto",
        "@startup_os//common",
        "@startup_os//common/flags",
        "@startup_os//common:dagger_with_annotation_processor",
        "//third_party/maven/com/google/guava",
        "//third_party/maven/com/google/protobuf:protobuf_java",
        "//third_party/maven/javax/inject:javax_inject",
        "//third_party/maven/org/slf4j:slf4j_api",
        "//third_party/maven/org/slf4j:slf4j_simple",
        "//third_party/maven/com/google/flogger:flogger",
        "//third_party/maven/com/google/flogger:flogger_system_backend",
        "//third_party/maven/org/apache/commons:commons_csv",
    ],
)
