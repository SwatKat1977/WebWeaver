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

#ifndef STUDIOSTATECONTROLLER_H_
#define STUDIOSTATECONTROLLER_H_
#include <functional>

namespace webweaver::studio {

enum class StudioState {
    NoProject,
    ProjectLoaded,
    RecordingRunning,
    RecordingPaused,
    Inspecting
};

class StudioStateController {
 public:
    using StateChangedCallback = std::function<void(StudioState)>;

    explicit StudioStateController(StateChangedCallback cb);

    StudioState GetState() const;

    void SetUiReady(bool ready) { uiReady_ = ready; }

    // User intents
    void OnSolutionLoaded();
    void OnSolutionClosed();
    void OnRecordStartStop();
    void OnRecordPause();
    void OnInspectorToggle(bool shown);

 private:
    void SetState(StudioState newState);

    StudioState state_ = StudioState::NoProject;
    StateChangedCallback onStateChanged_;
    bool uiReady_ = false;
};

}   // namespace webweaver::studio

#endif  // STUDIOSTATECONTROLLER_H_
