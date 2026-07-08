package com.todayflow.app

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.todayflow.compatibility.CompatibilityRepository
import com.todayflow.compatibility.CompatibilityViewModel
import com.todayflow.meaning.MeaningEventTracker

class CompatibilityViewModelFactory(
    private val repository: CompatibilityRepository,
    private val meaningTracker: MeaningEventTracker,
    private val authTokenProvider: () -> String?,
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(CompatibilityViewModel::class.java)) {
            return CompatibilityViewModel(repository, meaningTracker, authTokenProvider) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
