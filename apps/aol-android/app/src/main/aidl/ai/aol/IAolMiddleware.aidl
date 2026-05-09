// IAolMiddleware.aidl
//
// AIDL surface for the OEM AI assistant (Moto AI, Galaxy AI, OxygenOS AI ...)
// to talk to the AOL middleware. Three RPCs, no chatty per-frame methods.
//
// Bundle is used (rather than @Parcelable data classes) so that fields can be
// added forward-compatibly without recompiling the OEM AI assistant.

package ai.aol;

interface IAolMiddleware {

    /**
     * Filter / re-order the AI feature surface that the OEM assistant is
     * about to display.
     *
     * @param featureIds  Ordered list of every AI feature the assistant
     *                    *would* surface by default.
     * @param context     Bundle with optional keys:
     *                      - "time_of_day"  : "morning"|"midday"|"evening"|"night"
     *                      - "activity"     : "commute"|"work"|"meeting"|"leisure"|...
     *                      - "battery_pct"  : int 0..100
     *                      - "data_saver"   : boolean
     * @return Bundle with: visible, hide_recommended, user_disabled, rules_version.
     */
    Bundle filterSurface(in List<String> featureIds, in Bundle context);

    /**
     * Decide whether to run a feature on-device (local) or in the cloud.
     *
     * @param featureId   The feature about to be invoked.
     * @param hints       Bundle with optional keys: payload_kb, battery_pct,
     *                    private_mode.
     * @return Bundle with: decision, reason, chosen_ms, alt_ms, cost_usd.
     */
    Bundle routeCompute(String featureId, in Bundle hints);

    /**
     * Record an outcome / feedback. One-way / fire-and-forget.
     */
    oneway void recordOutcome(in Bundle event);
}
