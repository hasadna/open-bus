java_library(
    name = "jackson_annotations",
    exports = [
        "//external:jar/com/fasterxml/jackson/core/jackson_annotations"
    ],
    licenses = [
        "permissive"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "jackson_core",
    exports = [
        "//external:jar/com/fasterxml/jackson/core/jackson_core"
    ],
    licenses = [
        "permissive"
    ],
    visibility = [
        "//visibility:public"
    ]
)



java_library(
    name = "jackson_databind",
    exports = [
        "//external:jar/com/fasterxml/jackson/core/jackson_databind"
    ],
    licenses = [
        "permissive"
    ],
    runtime_deps = [
        ":jackson_annotations",
        ":jackson_core"
    ],
    visibility = [
        "//visibility:public"
    ]
)


