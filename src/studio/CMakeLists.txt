# Find wxWidgets via Homebrew
find_package(wxWidgets REQUIRED COMPONENTS core base aui)

include(${wxWidgets_USE_FILE})

add_executable(webweaver_studio
    BitmapUtils.cpp
    FilesystemUtils.cpp
    Platform.cpp
    RecentSolutionsManager.cpp
    RecordingMetadata.cpp
    RecordingViewerPanel.cpp
    SolutionExplorerIcons.cpp
    SolutionExplorerPanel.cpp
    studio.cpp
    StudioMainFrame.cpp
    StudioSolution.cpp
    StudioStateController.cpp
    ToolbarIcons.cpp
    UUID.cpp
    WizardStepIndicator.cpp
    WorkspacePanel.cpp
    recording/RecordingSession.cpp
    SolutionCreateWizard/BrowserIcons.cpp
    SolutionCreateWizard/WizardBasicInfoPage.cpp
    SolutionCreateWizard/WizardBehaviourPage.cpp
    SolutionCreateWizard/WizardFinishPage.cpp
    SolutionCreateWizard/WizardSelectBrowserPage.cpp
)

if(WIN32)
    target_compile_definitions(webweaver_studio PRIVATE WEBWEAVER_PLATFORM_WIN64)
elseif(APPLE)
    target_compile_definitions(webweaver_studio PRIVATE WEBWEAVER_PLATFORM_MACOS)
elseif(UNIX)
    target_compile_definitions(webweaver_studio PRIVATE WEBWEAVER_PLATFORM_LINUX)
endif()

target_include_directories(webweaver_studio PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ProjectCreate
)

target_include_directories(webweaver_studio PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../3rd_party
)

target_link_libraries(webweaver_studio
    ${wxWidgets_LIBRARIES}
)
