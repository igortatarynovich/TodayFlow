package com.todayflow.compatibility

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.todayflow.account.CompactUserModelInterpretationInstance
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext

private val Paper = Color(0xFFF6F5F2)
private val Sand = Color(0xFF8B7355)
private val Ink = Color(0xFF1F2937)
private val Sunset = Color(0xFFC97A35)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CompatibilityNavHost(
    viewModel: CompatibilityViewModel,
) {
    val uiState by viewModel.uiState.collectAsState()
    val showAnalyze = uiState.selected != null

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        if (showAnalyze) {
                            uiState.selected?.label ?: CompatibilityChrome.analyzeTitle
                        } else {
                            CompatibilityChrome.navTitle
                        },
                    )
                },
                navigationIcon = {
                    if (showAnalyze) {
                        TextButton(onClick = viewModel::clearSelection) {
                            Text(CompatibilityChrome.back)
                        }
                    }
                },
            )
        },
        containerColor = Paper,
    ) { padding ->
        if (showAnalyze) {
            CompatibilityAnalyzeScreen(
                modifier = Modifier.padding(padding),
                uiState = uiState,
                viewModel = viewModel,
            )
        } else {
            CompatibilityEncyclopediaScreen(
                modifier = Modifier.padding(padding),
                uiState = uiState,
                onRetry = viewModel::loadEncyclopedia,
                onSelect = viewModel::selectTopic,
            )
        }
    }
}

@Composable
fun CompatibilityEncyclopediaScreen(
    modifier: Modifier = Modifier,
    uiState: CompatibilityUiState,
    onRetry: () -> Unit,
    onSelect: (EncyclopediaAnalyzeSelection) -> Unit,
) {
    val catalog = uiState.catalog

    when {
        uiState.catalogLoading && catalog == null -> {
            Column(
                modifier = modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                CircularProgressIndicator(color = Sunset)
                Spacer(modifier = Modifier.height(12.dp))
                Text(CompatibilityChrome.loading, color = Ink.copy(alpha = 0.6f))
            }
        }

        catalog == null -> {
            Column(
                modifier = modifier.fillMaxSize().padding(24.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(uiState.catalogError ?: CompatibilityChrome.loadError, color = Ink)
                Spacer(modifier = Modifier.height(12.dp))
                Button(onClick = onRetry) { Text(CompatibilityChrome.retry) }
            }
        }

        else -> {
            LazyColumn(
                modifier = modifier.fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                item {
                    HeroCard(catalog.hero)
                }
                item {
                    Text(CompatibilityChrome.exploreTitle, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                }
                item {
                    LazyVerticalGrid(
                        columns = GridCells.Fixed(2),
                        modifier = Modifier.height(420.dp),
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                        userScrollEnabled = false,
                    ) {
                        items(catalog.categories.take(12)) { category ->
                            CategoryCard(category) {
                                onSelect(CompatibilitySelectionMapper.fromCategory(category))
                            }
                        }
                    }
                }
                item {
                    Text(CompatibilityChrome.popularTitle, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                }
                items(catalog.popularReadings.take(6)) { reading ->
                    ReadingCard(reading.title) {
                        onSelect(CompatibilitySelectionMapper.fromReading(reading))
                    }
                }
                item {
                    Text(CompatibilityChrome.seriesTitle, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                }
                items(catalog.series.take(8)) { series ->
                    SeriesCard(series) {
                        onSelect(CompatibilitySelectionMapper.fromSeries(series))
                    }
                }
            }
        }
    }
}

@Composable
private fun HeroCard(hero: CompatibilityEncyclopediaHero) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        shape = RoundedCornerShape(24.dp),
    ) {
        Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(hero.eyebrow.uppercase(), color = Sand, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.SemiBold)
            Text(hero.title, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = Ink)
            Text(hero.lead, style = MaterialTheme.typography.bodyMedium, color = Ink.copy(alpha = 0.68f))
        }
    }
}

@Composable
private fun CategoryCard(
    category: CompatibilityEncyclopediaCategory,
    onClick: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.92f)),
        shape = RoundedCornerShape(16.dp),
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(category.emoji, style = MaterialTheme.typography.headlineSmall)
            Text(category.title, fontWeight = FontWeight.SemiBold, color = Ink)
            Text(category.subtitle, style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.6f))
        }
    }
}

@Composable
private fun ReadingCard(
    title: String,
    onClick: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.92f)),
        shape = RoundedCornerShape(14.dp),
    ) {
        Text(
            title,
            modifier = Modifier.padding(12.dp),
            fontWeight = FontWeight.Medium,
            color = Ink,
        )
    }
}

@Composable
private fun SeriesCard(
    series: CompatibilityEncyclopediaSeries,
    onClick: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.92f)),
        shape = RoundedCornerShape(14.dp),
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(series.title, fontWeight = FontWeight.SemiBold, color = Ink)
            Text(series.subtitle, style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.62f))
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CompatibilityAnalyzeScreen(
    modifier: Modifier = Modifier,
    uiState: CompatibilityUiState,
    viewModel: CompatibilityViewModel,
) {
    val selection = uiState.selected ?: return
    val useRu = CompatibilityChrome.useRussian()

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            SelectionBanner(selection)
        }
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.95f)),
                shape = RoundedCornerShape(22.dp),
            ) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    Text(CompatibilityChrome.analyzeTitle, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)

                    SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
                        AnalyzeEntryMode.entries.forEachIndexed { index, mode ->
                            SegmentedButton(
                                selected = uiState.entryMode == mode,
                                onClick = { viewModel.setEntryMode(mode) },
                                shape = SegmentedButtonDefaults.itemShape(index = index, count = AnalyzeEntryMode.entries.size),
                            ) {
                                Text(
                                    when (mode) {
                                        AnalyzeEntryMode.QUICK -> CompatibilityChrome.quickEntry
                                        AnalyzeEntryMode.PRECISE -> CompatibilityChrome.preciseEntry
                                    },
                                )
                            }
                        }
                    }

                    if (uiState.entryMode == AnalyzeEntryMode.QUICK) {
                        SignDropdown(
                            label = CompatibilityChrome.yourSign,
                            selected = uiState.signFrom,
                            onSelected = viewModel::setSignFrom,
                            useRussian = useRu,
                        )
                        SignDropdown(
                            label = CompatibilityChrome.partnerSign,
                            selected = uiState.signTo,
                            onSelected = viewModel::setSignTo,
                            useRussian = useRu,
                        )
                        ContextDropdown(
                            label = CompatibilityChrome.betweenYou,
                            selected = uiState.relationshipContext,
                            onSelected = viewModel::setRelationshipContext,
                            useRussian = useRu,
                        )
                    } else {
                        OutlinedTextField(
                            value = uiState.birthDate1,
                            onValueChange = viewModel::setBirthDate1,
                            label = { Text(CompatibilityChrome.yourBirthdate) },
                            modifier = Modifier.fillMaxWidth(),
                            placeholder = { Text("YYYY-MM-DD") },
                        )
                        OutlinedTextField(
                            value = uiState.birthDate2,
                            onValueChange = viewModel::setBirthDate2,
                            label = { Text(CompatibilityChrome.partnerBirthdate) },
                            modifier = Modifier.fillMaxWidth(),
                            placeholder = { Text("YYYY-MM-DD") },
                        )
                    }

                    OutlinedTextField(
                        value = uiState.name1,
                        onValueChange = viewModel::setName1,
                        label = { Text(CompatibilityChrome.nameYou) },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = uiState.name2,
                        onValueChange = viewModel::setName2,
                        label = { Text(CompatibilityChrome.namePartner) },
                        modifier = Modifier.fillMaxWidth(),
                    )

                    Button(
                        onClick = viewModel::runDynamics,
                        enabled = !uiState.dynamicsLoading,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(if (uiState.dynamicsLoading) CompatibilityChrome.calculating else CompatibilityChrome.runReading)
                    }

                    uiState.dynamicsError?.let { error ->
                        Text(error, color = Color(0xFF991B1B), style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }

        uiState.dynamicsResult?.let { result ->
            item {
                DynamicsResultCard(
                    result = result,
                    ilrInstance = uiState.compatIlrInstance,
                    onAttachmentConfirm = viewModel::trackAttachmentLensConfirm,
                    onIlrInstanceConfirm = viewModel::trackInterpretationInstanceConfirm,
                )
            }
        }
    }
}

@Composable
private fun SelectionBanner(selection: EncyclopediaAnalyzeSelection) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFFFFBF5)),
        shape = RoundedCornerShape(22.dp),
    ) {
        Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(
                CompatibilityChrome.analyzeInvestigation.uppercase(),
                color = Sand,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.SemiBold,
            )
            Text(selection.label, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = Ink)
            selection.introBlocks.forEach { block -> IntroBlockView(block) }
            selection.scenarioBullets.forEach { bullet ->
                Text("• $bullet", style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.72f))
            }
        }
    }
}

@Composable
private fun IntroBlockView(block: EncyclopediaIntroBlock) {
    when (block.kind) {
        "question" ->
            block.text?.takeIf { it.isNotBlank() }?.let {
                Text(it, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium, color = Ink.copy(alpha = 0.82f))
            }
        "bullet_list" ->
            block.items.orEmpty().forEach { item ->
                Text("• $item", style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.72f))
            }
        else ->
            block.text?.takeIf { it.isNotBlank() }?.let {
                Text(it, style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.72f))
            }
    }
}

@Composable
private fun DynamicsResultCard(
    result: SignCompatibilityResponse,
    ilrInstance: CompactUserModelInterpretationInstance?,
    onAttachmentConfirm: (code: String, label: String, summary: String, echo: String, knowledgeId: String) -> Unit,
    onIlrInstanceConfirm: (instanceId: String, interpretationRefId: String?, summary: String, echo: String) -> Unit,
) {
    val surface = result.productSurface
    val attachmentHint = result.attachmentReference?.attachmentStyleHints?.firstOrNull()
    var dismissed by remember(attachmentHint?.code) { mutableStateOf(false) }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.95f)),
        shape = RoundedCornerShape(22.dp),
    ) {
        Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text("${result.fromSignName} × ${result.toSignName}", fontWeight = FontWeight.Bold, color = Ink)
                    surface?.scoreTagline?.let {
                        Text(it, style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.72f))
                    }
                }
                Text("${result.score}%", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = Sunset)
            }

            surface?.overviewParagraphs.orEmpty().forEach { paragraph ->
                Text(paragraph, style = MaterialTheme.typography.bodyMedium, color = Ink.copy(alpha = 0.78f))
            }

            surface?.blocks?.takeIf { it.isNotEmpty() }?.let { blocks ->
                Text(CompatibilityChrome.layers, fontWeight = FontWeight.Bold, color = Ink)
                blocks.forEach { block ->
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .background(Color(0xFFF8F6F2), RoundedCornerShape(14.dp))
                                .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        Text(block.title, fontWeight = FontWeight.SemiBold, color = Ink)
                        Text(block.subtitle, style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.55f))
                        Text(block.takeaway, fontWeight = FontWeight.Medium, color = Ink)
                        Text(block.detail, style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.78f))
                    }
                }
            }
        }
    }
}

@Composable
private fun AttachmentLensChip(
    hint: AttachmentStyleHint,
    onConfirm: (echo: String) -> Unit,
) {
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .background(Color(0xFFFFFBF5), RoundedCornerShape(16.dp))
                .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            "Возможный паттерн · не диагноз",
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.SemiBold,
            color = Sand,
        )
        Text(hint.label, fontWeight = FontWeight.Bold, color = Ink)
        Text(hint.summary, style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.72f))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf("yes" to "Точно", "partial" to "Частично", "no" to "Не про меня").forEach { (id, label) ->
                TextButton(onClick = { onConfirm(id) }) { Text(label) }
            }
        }
    }
}

private const val COMPAT_ILR_DISMISS_PREFIX = "todayflow.compat_ilr_instance.dismiss.v1"

@Composable
private fun IlrInstanceChip(
    instance: CompactUserModelInterpretationInstance,
    onConfirm: (echo: String) -> Unit,
) {
    val context = LocalContext.current
    val instanceId = instance.instanceId.orEmpty()
    val dismissKey = "$COMPAT_ILR_DISMISS_PREFIX.$instanceId"
    val prefs = remember { context.getSharedPreferences("todayflow_ilr_dismiss", Context.MODE_PRIVATE) }
    var dismissed by remember(instanceId) { mutableStateOf(prefs.contains(dismissKey)) }

    if (dismissed || instance.summary.isNullOrBlank()) return

    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .background(Color(0xFFFFFBF5), RoundedCornerShape(16.dp))
                .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            "Паттерн из твоих откликов · не вывод",
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.SemiBold,
            color = Sand,
        )
        Text(instance.summary, style = MaterialTheme.typography.bodySmall, color = Ink.copy(alpha = 0.78f))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf("yes" to "Точно", "partial" to "Частично", "no" to "Не про меня").forEach { (id, label) ->
                TextButton(
                    onClick = {
                        dismissed = true
                        prefs.edit().putString(dismissKey, id).apply()
                        onConfirm(id)
                    },
                ) { Text(label) }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SignDropdown(
    label: String,
    selected: ZodiacSign,
    onSelected: (ZodiacSign) -> Unit,
    useRussian: Boolean,
) {
    var expanded = remember { mutableStateOf(false) }
    androidx.compose.material3.ExposedDropdownMenuBox(
        expanded = expanded.value,
        onExpandedChange = { expanded.value = !expanded.value },
    ) {
        OutlinedTextField(
            value = selected.title(useRussian),
            onValueChange = {},
            readOnly = true,
            label = { Text(label) },
            modifier = Modifier.menuAnchor().fillMaxWidth(),
        )
        androidx.compose.material3.DropdownMenu(
            expanded = expanded.value,
            onDismissRequest = { expanded.value = false },
        ) {
            ZodiacSign.entries.forEach { sign ->
                androidx.compose.material3.DropdownMenuItem(
                    text = { Text(sign.title(useRussian)) },
                    onClick = {
                        onSelected(sign)
                        expanded.value = false
                    },
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ContextDropdown(
    label: String,
    selected: RelationshipContext?,
    onSelected: (RelationshipContext?) -> Unit,
    useRussian: Boolean,
) {
    var expanded = remember { mutableStateOf(false) }
    androidx.compose.material3.ExposedDropdownMenuBox(
        expanded = expanded.value,
        onExpandedChange = { expanded.value = !expanded.value },
    ) {
        OutlinedTextField(
            value = selected?.label(useRussian) ?: CompatibilityChrome.contextUnspecified,
            onValueChange = {},
            readOnly = true,
            label = { Text(label) },
            modifier = Modifier.menuAnchor().fillMaxWidth(),
        )
        androidx.compose.material3.DropdownMenu(
            expanded = expanded.value,
            onDismissRequest = { expanded.value = false },
        ) {
            androidx.compose.material3.DropdownMenuItem(
                text = { Text(CompatibilityChrome.contextUnspecified) },
                onClick = {
                    onSelected(null)
                    expanded.value = false
                },
            )
            RelationshipContext.entries.forEach { ctx ->
                androidx.compose.material3.DropdownMenuItem(
                    text = { Text(ctx.label(useRussian)) },
                    onClick = {
                        onSelected(ctx)
                        expanded.value = false
                    },
                )
            }
        }
    }
}
