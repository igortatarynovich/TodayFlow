package com.todayflow.today

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

@Composable
fun TodayContractScreen(
    repository: TodayRepository,
    modifier: Modifier = Modifier,
) {
    var contract by remember { mutableStateOf<TodayContractV1?>(null) }
    var loading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(repository) {
        loading = true
        error = null
        contract =
            withContext(Dispatchers.IO) {
                runCatching { repository.fetchTodayContract() }.getOrNull()
            }
        if (contract == null) {
            error = "Не удалось загрузить контракт дня"
        }
        loading = false
    }

    Column(
        modifier =
            modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Сегодня", style = MaterialTheme.typography.headlineMedium)
        when {
            loading -> CircularProgressIndicator()
            contract != null -> {
                val c = contract!!
                Text(c.themeHeadline(), style = MaterialTheme.typography.titleLarge)
                c.dayStory?.story?.takeIf { it.isNotBlank() }?.let {
                    Text(it, style = MaterialTheme.typography.bodyLarge)
                }
                Text("Главный шаг", style = MaterialTheme.typography.titleMedium)
                Text(
                    c.dayStory?.todayMove?.takeIf { it.isNotBlank() } ?: c.primaryAction,
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text("Отношения", style = MaterialTheme.typography.titleSmall)
                Text(c.domains.relationships.action, style = MaterialTheme.typography.bodyMedium)
                Text("Работа и деньги", style = MaterialTheme.typography.titleSmall)
                Text(c.domains.moneyWork.action, style = MaterialTheme.typography.bodyMedium)
                Text("Семья", style = MaterialTheme.typography.titleSmall)
                Text(c.domains.family.action, style = MaterialTheme.typography.bodyMedium)
            }
            else -> Text(error ?: "Нет данных", color = MaterialTheme.colorScheme.error)
        }
    }
}
