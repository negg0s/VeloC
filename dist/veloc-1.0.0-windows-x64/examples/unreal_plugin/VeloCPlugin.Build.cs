// VeloCPlugin.Build.cs
// Unreal Engine Module Rules integrating VeloC as a ThirdParty Native Library

using System.IO;
using UnrealBuildTool;

public class VeloCPlugin : ModuleRules
{
    public VeloCPlugin(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicIncludePaths.AddRange(new string[] {
            Path.Combine(ModuleDirectory, "Public")
        });

        // Link ThirdParty VeloC Library
        string ThirdPartyPath = Path.Combine(ModuleDirectory, "..", "ThirdParty", "VeloCLibrary");
        PublicIncludePaths.Add(Path.Combine(ThirdPartyPath, "include"));

        if (Target.Platform == UnrealTargetPlatform.Win64)
        {
            string LibPath = Path.Combine(ThirdPartyPath, "lib", "Win64", "veloc_physics.lib");
            PublicAdditionalLibraries.Add(LibPath);
            PublicDefinitions.Add("WITH_VELOC=1");
        }
    }
}
