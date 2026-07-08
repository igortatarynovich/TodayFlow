package com.todayflow.compatibility

import org.junit.Assert.assertEquals
import org.junit.Test

class CompatibilitySelectionMapperTest {
    @Test
    fun mapsCategorySelectionWithTopicId() {
        val category =
            CompatibilityEncyclopediaCategory(
                id = "love",
                emoji = "❤️",
                title = "Любовь",
                subtitle = "sub",
                analyzeParams = EncyclopediaAnalyzeParams(topic = "love"),
                introBlocks = listOf(EncyclopediaIntroBlock(kind = "paragraph", text = "Intro")),
            )
        val selection = CompatibilitySelectionMapper.fromCategory(category)
        assertEquals("love", selection.topicId)
        assertEquals("category", selection.selectionKind)
        assertEquals(1, selection.introBlocks.size)
    }

    @Test
    fun mapsSeriesWithScenarioBullets() {
        val series =
            CompatibilityEncyclopediaSeries(
                id = "office",
                title = "Office",
                subtitle = "sub",
                analyzeParams = EncyclopediaAnalyzeParams(series = "office"),
                scenarioBullets = listOf("A", "B"),
            )
        val selection = CompatibilitySelectionMapper.fromSeries(series)
        assertEquals("office", selection.seriesId)
        assertEquals(2, selection.scenarioBullets.size)
    }
}
