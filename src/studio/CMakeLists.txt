# Find wxWidgets via Homebrew
find_package(wxWidgets REQUIRED COMPONENTS core base aui)

include(${wxWidgets_USE_FILE})

add_executable(webweaver_studio
    BitmapUtils.cpp
    studio.cpp
    StudioMainFrame.cpp
    ToolbarIcons.cpp
    WizardStepIndicator.cpp
    ProjectCreateWizard/BrowserIcons.cpp
    ProjectCreateWizard/WizardBasicInfoPage.cpp
    ProjectCreateWizard/WizardBehaviourPage.cpp
    ProjectCreateWizard/WizardFinishPage.cpp
    ProjectCreateWizard/WizardSelectBrowserPage.cpp
)

target_include_directories(webweaver_studio PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ProjectCreate
)

target_link_libraries(webweaver_studio
    ${wxWidgets_LIBRARIES}
)
