/*
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

    This program is free software : you can redistribute it and /or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
*/
#include <utility>
#include "StudioStateController.h"

namespace webweaver::studio {

StudioStateController::StudioStateController(StateChangedCallback cb)
    : onStateChanged_(std::move(cb)) {
}

StudioState StudioStateController::GetState() const {
    return state_;
}

void StudioStateController::SetState(StudioState newState) {
    if (state_ == newState) {
        return;
    }
    state_ = newState;
    if (onStateChanged_) {
        onStateChanged_(state_);
    }
}

void StudioStateController::OnProjectLoaded() {
    SetState(StudioState::ProjectLoaded);
}

void StudioStateController::OnRecordStartStop() {
    if (state_ == StudioState::RecordingRunning ||
        state_ == StudioState::RecordingPaused) {
        SetState(StudioState::ProjectLoaded);
    } else if (state_ == StudioState::ProjectLoaded) {
        SetState(StudioState::RecordingRunning);
    }
}

void StudioStateController::OnRecordPause() {
    if (state_ == StudioState::RecordingRunning) {
        SetState(StudioState::RecordingPaused);
    } else if (state_ == StudioState::RecordingPaused) {
        SetState(StudioState::RecordingRunning);
    }
}

void StudioStateController::OnInspectorToggle(bool shown) {
    if (shown) {
        SetState(StudioState::Inspecting);
    } else {
        SetState(StudioState::ProjectLoaded);
    }
}

}   // namespace webweaver::studio
