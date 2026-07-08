package com.todayflow.account

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class InterpretationInstanceFiltersTest {
    @Test
    fun pendingCompatInstance_returnsFirstOpenCompatRow() {
        val rows =
            listOf(
                CompactUserModelInterpretationInstance(
                    instanceId = "inst-1",
                    interpretationRefId = "beh.today_echo_yes.v1",
                    summary = "Today pattern",
                ),
                CompactUserModelInterpretationInstance(
                    instanceId = "inst-2",
                    interpretationRefId = "beh.compat_echo_yes.v1",
                    summary = "Compat pattern",
                ),
            )

        val pending = InterpretationInstanceFilters.pendingCompatInstance(rows)
        assertEquals("inst-2", pending?.instanceId)
    }

    @Test
    fun pendingCompatInstance_skipsVerdictRows() {
        val rows =
            listOf(
                CompactUserModelInterpretationInstance(
                    instanceId = "inst-1",
                    interpretationRefId = "beh.compat_echo_yes.v1",
                    summary = "Done",
                    userVerdict = "confirm",
                ),
            )

        assertNull(InterpretationInstanceFilters.pendingCompatInstance(rows))
    }
}
