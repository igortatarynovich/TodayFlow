package com.todayflow.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.todayflow.compatibility.CompatibilityNavHost
import com.todayflow.compatibility.CompatibilityRepository
import com.todayflow.compatibility.CompatibilityViewModel
import com.todayflow.meaning.MeaningEventTracker
import com.todayflow.network.ApiClient
import com.todayflow.today.TodayCompositionScreen
import com.todayflow.today.TodayRepository

/**
 * Native Android shell — Today contract + Compatibility parity with web/iOS.
 */
class MainActivity : ComponentActivity() {
    private val meaningTracker by lazy { MeaningEventTracker(applicationContext) }

    private val compatibilityViewModel: CompatibilityViewModel by viewModels {
        CompatibilityViewModelFactory(
            repository =
                CompatibilityRepository(
                    authTokenProvider = {
                        getSharedPreferences(PREFS, MODE_PRIVATE).getString(KEY_AUTH_TOKEN, null)
                    },
                ),
            meaningTracker = meaningTracker,
            authTokenProvider = {
                getSharedPreferences(PREFS, MODE_PRIVATE).getString(KEY_AUTH_TOKEN, null)
            },
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val todayRepository =
            TodayRepository(
                api = ApiClient.service,
                authTokenProvider = {
                    getSharedPreferences(PREFS, MODE_PRIVATE).getString(KEY_AUTH_TOKEN, null)
                },
            )
        setContent {
            MaterialTheme(
                colorScheme =
                    lightColorScheme(
                        primary = androidx.compose.ui.graphics.Color(0xFFC97A35),
                    ),
            ) {
                var tab by remember { mutableIntStateOf(0) }
                Scaffold { padding ->
                    Column(
                        modifier =
                            Modifier
                                .fillMaxSize()
                                .padding(padding),
                    ) {
                        SingleChoiceSegmentedButtonRow(
                            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                        ) {
                            SegmentedButton(
                                selected = tab == 0,
                                onClick = { tab = 0 },
                                shape = SegmentedButtonDefaults.itemShape(index = 0, count = 2),
                            ) { Text("Сегодня") }
                            SegmentedButton(
                                selected = tab == 1,
                                onClick = { tab = 1 },
                                shape = SegmentedButtonDefaults.itemShape(index = 1, count = 2),
                            ) { Text("Совместимость") }
                        }
                        when (tab) {
                            0 -> TodayCompositionScreen(repository = todayRepository, modifier = Modifier.weight(1f))
                            else -> {
                                LaunchedEffect(Unit) {
                                    compatibilityViewModel.loadEncyclopedia()
                                }
                                CompatibilityNavHost(viewModel = compatibilityViewModel)
                            }
                        }
                    }
                }
            }
        }
    }

    companion object {
        const val PREFS = "todayflow_app"
        const val KEY_AUTH_TOKEN = "auth_token"
    }
}
