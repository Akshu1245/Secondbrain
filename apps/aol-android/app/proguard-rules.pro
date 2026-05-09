# Keep AIDL-generated stubs.
-keep class ai.aol.IAolMiddleware { *; }
-keep class ai.aol.IAolMiddleware$Stub { *; }

# Keep kotlinx.serialization @Serializable classes.
-keepclassmembers @kotlinx.serialization.Serializable class * {
    *** Companion;
}
-keepclasseswithmembers class * {
    kotlinx.serialization.KSerializer serializer(...);
}
