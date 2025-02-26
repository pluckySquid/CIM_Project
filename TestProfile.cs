using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Collections.Generic;
/**
 * Annotated C# for Profile
 * Generated by CIMTool https://cimtool.ucaiug.io
 */
public class Profile
{
       [Table("ACLineSegment")]
       public class ACLineSegment {
           public ACLineSegment() { }
           
           public override string ToString() { return this.GetType().Name; }
           
           [Column("mRID")]
           public string MRID { get; set; }
           [Column("aggregate")]
           public bool Aggregate { get; set; }
           [Column("aliasName")]
           public string AliasName { get; set; }
           [Column("b0ch")]
           public double B0ch { get; set; }
           [Column("bch")]
           public double Bch { get; set; }
           [Column("description")]
           public string Description { get; set; }
           [Column("g0ch")]
           public double G0ch { get; set; }
           [Column("gch")]
           public double Gch { get; set; }
           [Column("inService")]
           public bool InService { get; set; }
           [Column("length")]
           public double Length { get; set; }
           [Column("name")]
           public string Name { get; set; }
           [Column("networkAnalysisEnabled")]
           public bool NetworkAnalysisEnabled { get; set; }
           [Column("normallyInService")]
           public bool NormallyInService { get; set; }
           [Column("r")]
           public double R { get; set; }
           [Column("r0")]
           public double R0 { get; set; }
           [Column("shortCircuitEndTemperature")]
           public double ShortCircuitEndTemperature { get; set; }
           [Column("x")]
           public double X { get; set; }
           [Column("x0")]
           public double X0 { get; set; }
           [ForeignKey("_D5BE88A6-8696-43ec-A291-81AFED41113B-B")]
           public virtual ICollection<EquipmentUnavailabilitySchedule> _D5BE88A6_8696_43ec_A291_81AFED41113B_B { get; set; }
           [ForeignKey("ACLineSegmentPhases")]
           public virtual ICollection<ACLineSegmentPhase> ACLineSegmentPhases { get; set; }
           [ForeignKey("AdditionalEquipmentContainer")]
           public virtual ICollection<EquipmentContainer> AdditionalEquipmentContainer { get; set; }
           [ForeignKey("AssetDatasheet")]
           public virtual AssetInfo AssetDatasheet { get; set; }
           [ForeignKey("Assets")]
           public virtual ICollection<Asset> Assets { get; set; }
           [ForeignKey("BaseVoltage")]
           public virtual BaseVoltage BaseVoltage { get; set; }
           [ForeignKey("Clamp")]
           public virtual ICollection<Clamp> Clamp { get; set; }
           [ForeignKey("Clearances")]
           public virtual ICollection<ClearanceDocument> Clearances { get; set; }
           [ForeignKey("ConfigurationEvent")]
           public virtual ICollection<ConfigurationEvent> ConfigurationEvent { get; set; }
           [ForeignKey("ContingencyEquipment")]
           public virtual ICollection<ContingencyEquipment> ContingencyEquipment { get; set; }
           [ForeignKey("Controls")]
           public virtual ICollection<Control> Controls { get; set; }
           [ForeignKey("Cut")]
           public virtual ICollection<Cut> Cut { get; set; }
           [ForeignKey("DiagramObjects")]
           public virtual ICollection<DiagramObject> DiagramObjects { get; set; }
           [ForeignKey("EqiupmentLimitSeriesComponent")]
           public virtual ICollection<EquipmentLimitSeriesComponent> EqiupmentLimitSeriesComponent { get; set; }
           [ForeignKey("EquipmentContainer")]
           public virtual EquipmentContainer EquipmentContainer { get; set; }
           [ForeignKey("Faults")]
           public virtual ICollection<Fault> Faults { get; set; }
           [ForeignKey("GenericAction")]
           public virtual ICollection<GenericAction> GenericAction { get; set; }
           [ForeignKey("GroundingAction")]
           public virtual GroundAction GroundingAction { get; set; }
           [ForeignKey("InstanceSet")]
           public virtual InstanceSet InstanceSet { get; set; }
           [ForeignKey("JumpingAction")]
           public virtual JumperAction JumpingAction { get; set; }
           [ForeignKey("LimitDependencyModel")]
           public virtual ICollection<LimitDependency> LimitDependencyModel { get; set; }
           [ForeignKey("LineFaults")]
           public virtual ICollection<LineFault> LineFaults { get; set; }
           [ForeignKey("LineGroundingAction")]
           public virtual GroundAction LineGroundingAction { get; set; }
           [ForeignKey("LineJumpingAction")]
           public virtual JumperAction LineJumpingAction { get; set; }
           [ForeignKey("Location")]
           public virtual Location Location { get; set; }
           [ForeignKey("Measurements")]
           public virtual ICollection<Measurement> Measurements { get; set; }
           [ForeignKey("Names")]
           public virtual ICollection<Name> Names { get; set; }
           [ForeignKey("OperatingShare")]
           public virtual ICollection<OperatingShare> OperatingShare { get; set; }
           [ForeignKey("OperationalLimitSet")]
           public virtual ICollection<OperationalLimitSet> OperationalLimitSet { get; set; }
           [ForeignKey("OperationalRestrictions")]
           public virtual ICollection<OperationalRestriction> OperationalRestrictions { get; set; }
           [ForeignKey("OperationalTags")]
           public virtual ICollection<OperationalTag> OperationalTags { get; set; }
           [ForeignKey("Outage")]
           public virtual Outage Outage { get; set; }
           [ForeignKey("Outages")]
           public virtual ICollection<Outage> Outages { get; set; }
           [ForeignKey("PerLengthImpedance")]
           public virtual PerLengthImpedance PerLengthImpedance { get; set; }
           [ForeignKey("PinEquipment")]
           public virtual ICollection<PinEquipment> PinEquipment { get; set; }
           [ForeignKey("PropertiesCIMDataObject")]
           public virtual ChangeSetMember PropertiesCIMDataObject { get; set; }
           [ForeignKey("ProtectionEquipments")]
           public virtual ICollection<ProtectionEquipment> ProtectionEquipments { get; set; }
           [ForeignKey("ProtectiveActionAdjustment")]
           public virtual ICollection<ProtectiveActionAdjustment> ProtectiveActionAdjustment { get; set; }
           [ForeignKey("ProtectiveActionEquipment")]
           public virtual ICollection<ProtectiveActionEquipment> ProtectiveActionEquipment { get; set; }
           [ForeignKey("PSREvents")]
           public virtual ICollection<PSREvent> PSREvents { get; set; }
           [ForeignKey("PSRType")]
           public virtual PSRType PSRType { get; set; }
           [ForeignKey("ReportingGroup")]
           public virtual ICollection<ReportingGroup> ReportingGroup { get; set; }
           [ForeignKey("SvStatus")]
           public virtual ICollection<SvStatus> SvStatus { get; set; }
           [ForeignKey("TargetingCIMDataObject")]
           public virtual ICollection<ChangeSetMember> TargetingCIMDataObject { get; set; }
           [ForeignKey("Terminals")]
           public virtual ICollection<Terminal> Terminals { get; set; }
           [ForeignKey("UsagePoints")]
           public virtual ICollection<UsagePoint> UsagePoints { get; set; }
           [ForeignKey("VerificationAction")]
           public virtual ICollection<VerificationAction> VerificationAction { get; set; }
           [ForeignKey("WeatherStation")]
           public virtual ICollection<WeatherStation> WeatherStation { get; set; }
           [ForeignKey("WireSpacingInfo")]
           public virtual WireSpacingInfo WireSpacingInfo { get; set; }
       }
       [Table("ACLineSegmentPhase")]
       public class ACLineSegmentPhase {
           public ACLineSegmentPhase() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("AnalogLimit")]
       public class AnalogLimit {
           public AnalogLimit() { }
           
           public override string ToString() { return this.GetType().Name; }
           
           [Column("value")]
           public double Value { get; set; }
           [ForeignKey("LimitSet")]
           public virtual AnalogLimitSet LimitSet { get; set; }
       }
       [Table("AnalogLimitSet")]
       public class AnalogLimitSet {
           public AnalogLimitSet() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("Asset")]
       public class Asset {
           public Asset() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("AssetInfo")]
       public class AssetInfo {
           public AssetInfo() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("BaseVoltage")]
       public class BaseVoltage {
           public BaseVoltage() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("ChangeSetMember")]
       public class ChangeSetMember {
           public ChangeSetMember() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("ClearanceDocument")]
       public class ClearanceDocument {
           public ClearanceDocument() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("ConfigurationEvent")]
       public class ConfigurationEvent {
           public ConfigurationEvent() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("ContingencyEquipment")]
       public class ContingencyEquipment {
           public ContingencyEquipment() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("Control")]
       public class Control {
           public Control() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("DiagramObject")]
       public class DiagramObject {
           public DiagramObject() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("Equipment")]
       public class Equipment {
           public Equipment() { }
           
           public override string ToString() { return this.GetType().Name; }
           
           [Column("aggregate")]
           public bool Aggregate { get; set; }
           [Column("inService")]
           public bool InService { get; set; }
           [Column("networkAnalysisEnabled")]
           public bool NetworkAnalysisEnabled { get; set; }
           [Column("normallyInService")]
           public bool NormallyInService { get; set; }
           [ForeignKey("EquipmentContainer")]
           public virtual EquipmentContainer EquipmentContainer { get; set; }
       }
       [Table("EquipmentContainer")]
       public class EquipmentContainer {
           public EquipmentContainer() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("EquipmentLimitSeriesComponent")]
       public class EquipmentLimitSeriesComponent {
           public EquipmentLimitSeriesComponent() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("EquipmentUnavailabilitySchedule")]
       public class EquipmentUnavailabilitySchedule {
           public EquipmentUnavailabilitySchedule() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("Fault")]
       public class Fault {
           public Fault() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("GenericAction")]
       public class GenericAction {
           public GenericAction() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("GroundAction")]
       public class GroundAction {
           public GroundAction() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("InstanceSet")]
       public class InstanceSet {
           public InstanceSet() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("JumperAction")]
       public class JumperAction {
           public JumperAction() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("LimitDependency")]
       public class LimitDependency {
           public LimitDependency() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("Location")]
       public class Location {
           public Location() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("Measurement")]
       public class Measurement {
           public Measurement() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("Name")]
       public class Name {
           public Name() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("OperatingShare")]
       public class OperatingShare {
           public OperatingShare() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("OperationalLimitSet")]
       public class OperationalLimitSet {
           public OperationalLimitSet() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("OperationalRestriction")]
       public class OperationalRestriction {
           public OperationalRestriction() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("OperationalTag")]
       public class OperationalTag {
           public OperationalTag() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("Outage")]
       public class Outage {
           public Outage() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("PSREvent")]
       public class PSREvent {
           public PSREvent() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("PSRType")]
       public class PSRType {
           public PSRType() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("PinEquipment")]
       public class PinEquipment {
           public PinEquipment() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("ProtectionEquipment")]
       public class ProtectionEquipment : Equipment {
       // Inherits from Equipment - configure further in EF Fluent API if needed
           public ProtectionEquipment() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("ProtectiveActionAdjustment")]
       public class ProtectiveActionAdjustment {
           public ProtectiveActionAdjustment() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("ProtectiveActionEquipment")]
       public class ProtectiveActionEquipment {
           public ProtectiveActionEquipment() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("ReportingGroup")]
       public class ReportingGroup {
           public ReportingGroup() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("SvStatus")]
       public class SvStatus {
           public SvStatus() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("Terminal")]
       public class Terminal {
           public Terminal() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("UsagePoint")]
       public class UsagePoint {
           public UsagePoint() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("VerificationAction")]
       public class VerificationAction {
           public VerificationAction() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
       [Table("VoltageLevel")]
       public class VoltageLevel : EquipmentContainer {
       // Inherits from EquipmentContainer - configure further in EF Fluent API if needed
           public VoltageLevel() { }
           
           public override string ToString() { return this.GetType().Name; }
           
           [Column("highVoltageLimit")]
           public double HighVoltageLimit { get; set; }
           [Column("lowVoltageLimit")]
           public double LowVoltageLimit { get; set; }
           [ForeignKey("BaseVoltage")]
           public virtual BaseVoltage BaseVoltage { get; set; }
           [ForeignKey("Substation")]
           public virtual Substation Substation { get; set; }
       }
       [Table("WeatherStation")]
       public class WeatherStation {
           public WeatherStation() { }
           
           public override string ToString() { return this.GetType().Name; }
           
       }
        
       public static readonly System.Type[] allClasses = new System.Type[]
       {
           typeof(ACLineSegment),
           typeof(ACLineSegmentPhase),
           typeof(AnalogLimit),
           typeof(AnalogLimitSet),
           typeof(Asset),
           typeof(AssetInfo),
           typeof(BaseVoltage),
           typeof(ChangeSetMember),
           typeof(ClearanceDocument),
           typeof(ConfigurationEvent),
           typeof(ContingencyEquipment),
           typeof(Control),
           typeof(DiagramObject),
           typeof(Equipment),
           typeof(EquipmentContainer),
           typeof(EquipmentLimitSeriesComponent),
           typeof(EquipmentUnavailabilitySchedule),
           typeof(Fault),
           typeof(GenericAction),
           typeof(GroundAction),
           typeof(InstanceSet),
           typeof(JumperAction),
           typeof(LimitDependency),
           typeof(Location),
           typeof(Measurement),
           typeof(Name),
           typeof(OperatingShare),
           typeof(OperationalLimitSet),
           typeof(OperationalRestriction),
           typeof(OperationalTag),
           typeof(Outage),
           typeof(PSREvent),
           typeof(PSRType),
           typeof(PinEquipment),
           typeof(ProtectionEquipment),
           typeof(ProtectiveActionAdjustment),
           typeof(ProtectiveActionEquipment),
           typeof(ReportingGroup),
           typeof(SvStatus),
           typeof(Terminal),
           typeof(UsagePoint),
           typeof(VerificationAction),
           typeof(VoltageLevel),
           typeof(WeatherStation)
       };
}
