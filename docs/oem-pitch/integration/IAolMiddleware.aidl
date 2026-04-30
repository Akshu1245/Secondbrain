// IAolMiddleware.aidl
//
// Surface for the OEM AI assistant (Moto AI, Galaxy AI, OxygenOS AI, etc.) to
// talk to the AOL middleware. AOL ships as a Foreground Service in its own
// process and exposes the methods below over Binder.
//
// Why AIDL: it's the canonical, type-safe Android IPC surface for system
// services. Every OEM AI assistant team understands it, and it lets AOL run
// in a separate process with its own permissions / lifecycle.
//
// Design principles:
//   1. Small surface. Three RPCs, no chatty per-frame methods.
//   2. Bundle, not Parcelable. Bundles are forward-compatible — fields can be
//      added without recompiling the OEM AI assistant.
//   3. Synchronous responses with cheap rule-based bodies, so the OEM AI
//      assistant can call this on the UI thread of its launcher strip.
//
// See AolClient.kt for an end-to-end usage example.

package ai.aol;

interface IAolMiddleware {

    /**
     * Filter / re-order the AI feature surface that the OEM assistant is about
     * to display.
     *
     * @param featureIds  Ordered list of every AI feature the assistant *would*
     *                    surface by default (e.g. ["smart_reply", "magic_eraser",
     *                    "live_translate", ...]).
     * @param context     Bundle with optional keys:
     *                      - "time_of_day"  : "morning"|"midday"|"evening"|"night"
     *                      - "activity"     : "commute"|"work"|"meeting"|"leisure"|...
     *                      - "battery_pct"  : int 0..100
     *                      - "data_saver"   : boolean
     *
     * @return Bundle with:
     *           - "visible"           : String[]  (ordered, only what to show)
     *           - "hide_recommended"  : String[]  (still installed, just hidden)
     *           - "user_disabled"     : String[]  (explicit toggle-off)
     *           - "rules_version"     : int       (for telemetry)
     */
    Bundle filterSurface(in List<String> featureIds, in Bundle context);

    /**
     * Decide whether to run a feature on-device or in the cloud.
     *
     * @param featureId   The feature about to be invoked.
     * @param hints       Bundle with optional keys:
     *                      - "payload_kb"   : int (size of attached image,
     *                                              transcript, etc.)
     *                      - "battery_pct"  : int
     *                      - "private_mode" : boolean
     *
     * @return Bundle with:
     *           - "decision"   : "local"|"cloud"
     *           - "reason"     : human-readable explanation (for debug + the
     *                            user-facing Control Panel)
     *           - "chosen_ms"  : expected latency at the chosen path
     *           - "alt_ms"     : expected latency at the other path
     *           - "cost_usd"   : expected cloud cost (0.0 for local)
     */
    Bundle routeCompute(String featureId, in Bundle hints);

    /**
     * Record an outcome — success/failure of a feature invocation, or explicit
     * user feedback ("love"/"ok"/"annoying"/"never_use"). Drives the nightly
     * improvement loop without retraining any model.
     *
     * @param event Bundle with keys:
     *                - "feature_id" : String
     *                - "kind"       : "outcome"|"feedback"
     *                - "rating"     : optional, only for "feedback" events
     *                - "success"    : optional, only for "outcome" events
     *                - "ts_ms"      : long, epoch milliseconds
     */
    oneway void recordOutcome(in Bundle event);
}
