from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing_extensions import Annotated
from pathlib import Path
from pydantic import BaseModel


app = FastAPI()

app.mount(
        "/static",
        StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
        name="static",
          )

template= Jinja2Templates(directory="Templates")

#Base Class used to represent Devices
class Device(BaseModel):
    id: int
    deviceName: str
    ip: str


#Creating a starting list of Devices to  manipulate
device1 = Device(id=1, deviceName="RTR_Core_1", ip="192.168.0.1")
device2 = Device(id=2, deviceName="RTR_Dist_1", ip="192.168.0.2")
device3 = Device(id=3, deviceName="SW_Acc_1", ip="192.168.0.3")
deviceList = [device1, device2, device3]


#root
@app.get('/')
async def index(req: Request):
    return template.TemplateResponse(
        name="index.html",
        context={"request": req}
    )

#load device list
@app.get('/devices')
async def getDevices(req: Request):
    return template.TemplateResponse(
        request=req,
        name="list.html",
        context={"deviceList": deviceList}
    )

#add a device
@app.post('/devices')
async def addDevices(req: Request, deviceName: Annotated[str, Form()], ip: Annotated[str, Form()]):
    newDeviceName = deviceName
    newIP = ip
    newDevice = Device(id=len(deviceList)+1, deviceName=newDeviceName, ip=newIP)
    deviceList.append(newDevice)

    return RedirectResponse(url=f"/devices/{newDevice.id}", status_code=303)

#create a device
@app.get('/devices/{deviceID}')
async def getDevice(req: Request, deviceID: int):
    for device in deviceList:
        if deviceID == device.id:
            return template.TemplateResponse(
                request=req,
                name="device.html",
                context={"device": device}
            )
    raise HTTPException(status_code=404, detail="Device not found")

#delete a device
@app.delete('/devices/{deviceID}')
async def delDevice(req: Request, deviceID: int):
    for device in deviceList:
        if deviceID == device.id:
            deviceList.remove(device)
            return template.TemplateResponse(
                request=req,
                name="list.html",
                context={"device": device}
            )

    raise HTTPException(status_code=404, detail="Device not found")

#get a form to edit device
@app.get('/devices/edit/{deviceID}')
async def editDevice(req: Request, deviceID: int):
    for device in deviceList:
        if deviceID == device.id:
            editDevice = device
            return template.TemplateResponse(
                request=req,
                name="edit.html",
                context={"device": editDevice}
            )
    raise HTTPException(status_code=404, detail="Device not found")

#edit and replace a device
@app.put('/devices/{deviceID}')
async def putDevice(req: Request, deviceID: int, deviceName: Annotated[str, Form()], ip: Annotated[str, Form()]):
    index = 0
    editID = deviceID
    editDeviceName = deviceName
    editIP = ip
    editDevice = Device(id=editID, deviceName=editDeviceName, ip=editIP)

    for device in deviceList:
        if deviceID == device.id:

            deviceList[index] = editDevice

            return template.TemplateResponse(
                request=req,
                name="device.html",
                context={"device": editDevice}
            )

        index= index + 1

#search functionality
@app.post('/devices/search')
async def searchDevice(req: Request, searchEntry: str= Form()):

    search = searchEntry.lower()
    searchList = []
    for device in deviceList:
        if device.deviceName.lower().find(search) != -1:
            searchList.append(device)

    return template.TemplateResponse(
        request=req,
        name="list.html",
        context={"deviceList": searchList}
    )

