package ai.aol.demo

/**
 * The catalog of Moto AI features the demo recognises.
 *
 * Mirrors the Python reference implementation in `apps/aol/api/app/data/`.
 * The cost / latency numbers are the same calibrated figures used in
 * `docs/oem-pitch/moto-specific.md` so the Android side and the dashboard
 * agree on the headline "~45 % of calls land local".
 */
object FeatureCatalog {

    private data class Feature(
        val id: String,
        val priority: String,    // "core", "productivity", "creative", "wellbeing"
        val hasLocalPath: Boolean,
        val needsFreshKnowledge: Boolean,
        val isHeavyCloud: Boolean,
        val isInterrupting: Boolean,
        val localMs: Int,
        val cloudMs: Int,
        val perCallCloudUsd: Double,
    )

    private val features: Map<String, Feature> = listOf(
        // Moto AI named features (sourced from Lenovo's Smart Connect /
        // Moto AI feature inventory — see docs/oem-pitch/moto-specific.md).
        Feature("smart_reply",        "productivity", true,  false, false, false, 80,  420, 0.0008),
        Feature("catch_me_up",        "productivity", true,  false, false, false, 110, 380, 0.0011),
        Feature("pay_attention",      "productivity", false, true,  true,  true,  0,   650, 0.0023),
        Feature("remember_this",      "productivity", true,  false, false, false, 60,  300, 0.0007),
        Feature("magic_canvas",       "creative",     false, true,  true,  false, 0,   2400, 0.0084),
        Feature("image_studio",       "creative",     false, true,  true,  false, 0,   3100, 0.0102),
        Feature("magic_eraser",       "creative",     true,  false, false, false, 220, 880, 0.0019),
        Feature("live_translate",     "productivity", true,  false, false, false, 95,  340, 0.0009),
        Feature("circle_to_search",   "productivity", false, true,  false, false, 0,   520, 0.0014),
        Feature("next_move",          "productivity", true,  false, false, false, 70,  290, 0.0006),
        Feature("focus_mode",         "wellbeing",    true,  false, false, false, 30,  0,   0.0),
        Feature("wallpaper_studio",   "creative",     false, false, true,  false, 0,   2100, 0.0072),
    ).associateBy { it.id }

    fun priorityFor(id: String): String = features[id]?.priority ?: "productivity"
    fun hasLocalPath(id: String): Boolean = features[id]?.hasLocalPath ?: false
    fun requiresFreshKnowledge(id: String): Boolean = features[id]?.needsFreshKnowledge ?: false
    fun isHeavyCloud(id: String): Boolean = features[id]?.isHeavyCloud ?: false
    fun isInterrupting(id: String): Boolean = features[id]?.isInterrupting ?: false
    fun localMs(id: String): Int = features[id]?.localMs ?: 100
    fun cloudMs(id: String): Int = features[id]?.cloudMs ?: 500

    fun cloudCostUsd(id: String, payloadKb: Int): Double {
        val base = features[id]?.perCallCloudUsd ?: 0.001
        // Larger payloads get a small linear surcharge (token / pixel cost).
        return base * (1.0 + payloadKb / 256.0)
    }

    fun all(): List<String> = features.values.map { it.id }
}
