//
// This file was generated by the JavaTM Architecture for XML Binding(JAXB) Reference Implementation, vJAXB 2.1.10 in JDK 6 
// See <a href="http://java.sun.com/xml/jaxb">http://java.sun.com/xml/jaxb</a> 
// Any modifications to this file will be lost upon recompilation of the source schema. 
// Generated on: 2010.11.14 at 03:28:36 PM PST 
//


package uk.org.siri.siri;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlType;


/**
 * Type for Info Channel Permission.
 * 
 * <p>Java class for InfoChannelPermissionStructure complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="InfoChannelPermissionStructure">
 *   &lt;complexContent>
 *     &lt;extension base="{http://www.siri.org.uk/siri}AbstractTopicPermissionStructure">
 *       &lt;sequence>
 *         &lt;element name="InfoChannelRef" type="{http://www.siri.org.uk/siri}InfoChannelRefStructure"/>
 *       &lt;/sequence>
 *     &lt;/extension>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "InfoChannelPermissionStructure", propOrder = {
    "infoChannelRef"
})
public class InfoChannelPermissionStructure
    extends AbstractTopicPermissionStructure
{

    @XmlElement(name = "InfoChannelRef", required = true)
    protected InfoChannelRefStructure infoChannelRef;

    /**
     * Gets the value of the infoChannelRef property.
     * 
     * @return
     *     possible object is
     *     {@link InfoChannelRefStructure }
     *     
     */
    public InfoChannelRefStructure getInfoChannelRef() {
        return infoChannelRef;
    }

    /**
     * Sets the value of the infoChannelRef property.
     * 
     * @param value
     *     allowed object is
     *     {@link InfoChannelRefStructure }
     *     
     */
    public void setInfoChannelRef(InfoChannelRefStructure value) {
        this.infoChannelRef = value;
    }

}
